# Paderborn Bearing Package
This package is created to extract and preprocess the Paderborn bearing datasets provided by the [Paderborn University Faculty of Mechanical Engineering][paderborn].
This package is specifically designed to extract multivariate sensor readings from the MATLAB files containing different Bearing faults. The current version supports all operating systems, but keep in mind that you need different software packages installed depending on the operating system you use. 

### Dataset
The dataset consists of 25 damaged bearing states and 6 undamaged bearing states (Healthy condition). The damaged bearings are divided into artificial and real damages. Both of these damaged bearing states, two options are available where the damages are located, e.g., inner race (IR) and outer race (OR). One of the experiment types for the artificial OR condition is removed. 


### Installation
Installing the package can be done manually, but I recommend to install via pip since this is much easier by just copying the code below and paste it in your terminal/command prompt:
```sh
$ pip install paderborn-bearing
```
Please also check which dependencies are needed to use the package. 

### Use of the package
After the installation, the package can be imported in your specific session, for example in Jupyter Notebook;
```sh
from paderborn_bearing import *
```
Then the class in the package can be called as follows;
```sh
data = Paderborn("Artificial", 1024, "OR")
```
The called function results in three different objects:
* data.motor_current, contains all the samples represented in a 3D-array for the two motor current sensor readings related to the specific experiment and fault name. The lay-out of the array is as follows; nr of time series, sequence length, amount of sensors. 
* data.vibrations, contains all the samples represented in a 3D-array for the vibration sensor related to the specific experiment and fault name. The lay-out of the array is as follows; nr of time series, sequence length, amount of sensors. 
* data.labels, labels representing different fault conditions.

### Arguments
As can be seen in the previous code block, the package asks three arguments for extracting and preprocessing the Paderborn bearing datasets into usable objects. The following arguments need to be addressed when using Paderborn class:
>1) Experiment: A string value that indicates the specific name for the experiment to use. There are three options: `"Artificial"`, `"Healthy"` and `"Real"`.
>2) Length: an integer value that indicates the sequence length of every time series.
>3) Fault location: A string value that specifies the fault location of the bearing to narrow down the experiment's data. There are three options are available (Inner, Outer and Normal), `"IR"`,`"OR"` and `"Normal"`. For the "Artificial" and "Real" options both "IR" and "OR" can be combined. For the "Heathly" option only the "Normal" condition can be used.  

### Dependencies
The following dependencies are needed to get the package installed. Because the MATLAB files need to be unpacked, we use different packages depending on the operating system.
* numpy
* patool (Windows)
* scipy 
* subprocess (Mac OS/Linux)
* tqdm
* requests

### MacOS/Linux
Since the package wants to unpack .rar files, you first need to install [Homebrew][homebrew] in your terminal combined with [Unar][unar].

Paste this in a macOS Terminal to install Homebrew:
```sh
$/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Next, use the following command to install Unar:
```sh
$brew install unar
```

### Additional information
The objects that are created are extracted from many MATLAB files, resulting in large-scale arrays. Therefore, I would like to emphasise to create every object separately, e.g., one experiment option + one fault location option to reduce the computation time of the data preprocessing. Keep in mind that the creation of one of these objects might take approximately 10 minutes since the arrays have to be stacked together across a wide variety of files. This results in large-scale data object of at least 3GB per object. I would therefore recommend to save the objects after preprocessing as numpy arrays, so that when you want to apply ML or DL algorithms, you only need to load in the objects (and potentially concatenate them).  


[paderborn]: <https://mb.uni-paderborn.de/en/kat/main-research/datacenter/bearing-datacenter/data-sets-and-download>
[homebrew]: <https://brew.sh>
[unar]: <https://formulae.brew.sh/formula/unar#default>





