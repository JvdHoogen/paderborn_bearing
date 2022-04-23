#%%
import os,re
import glob
import errno
import random
import urllib.request 
import numpy as np
from scipy.io import loadmat
from sklearn.utils import shuffle
import sys
import time
from tqdm import tqdm
import subprocess

start_time = time.time()
class Paderborn:
    def __init__(self, experiment, seq_len, *bearing_element):

        if experiment not in ('Artificial', 'Healthy', 'Real'):
            print("wrong experiment name: {}".format(experiment))
            sys.exit(1) 
        # print(bearing_element)
        for i in bearing_element:
            if i not in ('OR', 'IR','Normal'): 
                print("wrong bearing element value: {}".format(bearing_element))
                sys.exit(1)
        # Root directory of all data and loading in text file
        rdir = os.path.join(os.path.expanduser('~'), 'Datasets/Paderborn')
        cur_path = os.path.dirname(__file__)
        fmeta = os.path.join(cur_path, "datafiles.txt")


        # Read text file and load all separate http addresses
        all_lines = open(fmeta).readlines() 
        lines = []
        for line in all_lines:
            l = line.split()
            if l[0] in experiment and l[1] in bearing_element:
                lines.append(l)

        self.seq_len = seq_len
        self.unpack_files(rdir, lines)
        self.read_matfiles(rdir, experiment,bearing_element)
        self.threshold_selector()
        self.data_divider()

    def slicer(self,time_series,seq_len):
        # Divide the data into sequences based on the sequence length and the length of the time series
        idx_last = -(time_series.shape[0] % seq_len)
        if idx_last < 0:
            clips = time_series[:idx_last].reshape(-1, seq_len)
        else:
            clips = time_series[idx_last:].reshape(-1, seq_len)
        return(clips)

    def most_frequent(self,list_values):
        return max(set(list_values), key = list_values.count)    

    def _mkdir(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                print("can't create directory '{}''".format(path))
                exit(1)
    def _download(self, fpath, link):
        print("Downloading to: '{}'".format(fpath))
        urllib.request.urlretrieve(link, fpath)

    def unpack_files(self, rdir, lines):
        for idx, info in enumerate(lines):
            # Directory of this file
            fdir = os.path.join(rdir, info[0], info[1])
            self._mkdir(fdir)
            fpath = os.path.join(fdir, info[2] + '.rar')
            if not os.path.exists(fpath):
                self._download(fpath, info[3])

            ab = os.chdir(fdir)
            ## Run a subprocess using homebrew combined with unar to unpack rar files downloaded from the Paderborn Bearing website. 
            list_files = subprocess.run(["unar",fpath])


    def read_matfiles(self,directory,experiment,bearing_element):
        y_divider = 0
        self.y_list = []
        directory = os.path.join(directory,experiment)
        self.empty_list = []
        file_name = []
        # Read .mat files based on the bearing element damage and the experiment name
        for paths, dirs, files in os.walk(directory):
            if paths.endswith(bearing_element):
                for paths, dirs, files in os.walk(paths):
                    for j in dirs:
                        y_divider += 1
                        print(y_divider)
                        self.y_list.append(1)
                    for i in files:
                        if '.mat' in i:
                            mat_dict = loadmat(os.path.join(paths,i))
                            file = mat_dict[list(mat_dict.keys())[-1]]
                            file_name.append(i)
                            
                            for index,i in enumerate(file[0][0]):
                                if index == 1:
                                    self.empty_list.append(i)
                                if index == 2:
                                    self.empty_list.append(i)
        # Calculate the amount of conditions for identifying the target values                                    
        self.y_files = int(len(file_name) / y_divider)


    def threshold_selector(self):
        threshold_list = []
        labels = []

        # Iterate over every file to receive the sensor values sampled at 64 KHz for approximately 4 seconds per file. Therefore every array should be longer than 200k datapoints
        for index,i in enumerate(self.empty_list,self.seq_len):
            for j in i:
                for i2 in j:
                    for i3 in i2:
                        for i4 in i3:
                            if len(i4) > 200000: # Arbitrary length based on the 64kHZ for 4 seconds
                                khz_64 = self.slicer(i4,self.seq_len)
                                threshold_list.append(len(khz_64))

        # Calculate threshold used to indentify the length of every array
        self.threshold = self.most_frequent(threshold_list)

        # Create a target value for every of the sequences in the data
        for index, ix in enumerate(self.y_list):
            labels.extend([index] * self.y_files * self.threshold)
        self.labels = np.array(labels)


    def data_divider(self):
        # Divide the data into sequences of a given length for the two motor current sensor data points and the seperately provided vibrations sensor readings. 
        time_khz64 = np.zeros((self.threshold,self.seq_len))
        self.motor_current = np.zeros((0,self.seq_len,2)) 
        self.vibration_sens = np.zeros((0,self.seq_len,1))
        y_64 = []
        indexer1 = 0
        for index,i in tqdm(enumerate(self.empty_list,self.seq_len)):
            for j in i:
                for i2 in j:
                    for i3 in i2:
                        for i4 in i3:
                            if len(i4) > 200000: # Arbitrary length based on the 64kHZ for 4 seconds
                                khz_64 = self.slicer(i4,self.seq_len)
                                if khz_64.shape[0] > self.threshold:
                                    khz_64 = khz_64[:self.threshold,]
                                if khz_64.shape[0] < self.threshold:
                                    repeater = self.threshold - khz_64.shape[0]
                                    c = np.repeat(khz_64[-1][None,:], repeater, axis=0)
                                    khz_64 = np.concatenate((khz_64,c))
                                time_khz64 = np.dstack((time_khz64, khz_64))
                                if time_khz64.shape[2] == 5:
                                    vibrations = time_khz64[:,:,4:5]
                                    motor_current = time_khz64[:,:,2:4]
                                    self.motor_current = np.vstack((self.motor_current,motor_current))
                                    self.vibration_sens = np.vstack((self.vibration_sens,vibrations))
                                    time_khz64 = np.zeros((self.threshold,self.seq_len))
print("--- %s seconds ---" % (time.time() - start_time))


