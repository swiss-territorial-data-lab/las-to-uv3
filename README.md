# Overview

This is writing uv3 files out of LiDAR data (.las). The most basic form is giving RGB values based on the file's **height** (Z values). This is already implemented, but other tools will soon be available too. This counts on colouring point cloud based on **classification** and **intensity** values. If your las file has already been coloured, this code with have a parameter allowing to use those RGB values instead. 

## las-to-uv3

For the moment, this is taking only LiDAR data in the Swiss Coordinate System (CH1903+ / LV95), but soon this is also turning into optional. As LiDAR files are usually big, this can be time-demanding, but won't make you run out of memory. For usage, simply open the folder where this code was cloned or downloaded and use the following command.

```
$ python3 las-to-uv3.py -i /home/user/path/to/las/file.las -o /home/user/path/to/output.uv3 
```
Antoher importat aspect is the range value for the height colouring. As default this is set to be 4800, which is the range in Switzerland elevation values. For now this can be changed in the raw code, but it will also be an optional argument.

## Other arguments

As explained, this is still being implemented, but future parameters will be:

### Classification

If you're willing to colour your las file based on classification values, this is the argument you should set as *True*, as in the example below. Sometimes classification values do not follow a general rule. If this is the case, you'll need to look in the raw code to change colours and classification values based on your specific case.

```
$ python3 las-to-uv3.py -i /home/user/path/to/las/file.las -o /home/user/path/to/output.uv3 -c True
```

### Intensity

If what you're really wanting to explore is intensity values, this is the argument you should set as *True*:

```
$ python3 las-to-uv3.py -i /home/user/path/to/las/file.las -o /home/user/path/to/output.uv3 -t True
``` 

### RGB

FInally, if you already have a coloured las file, you might choose this option:

```
$ python3 las-to-uv3.py -i /home/user/path/to/las/file.las -o /home/user/path/to/output.uv3 -r True
``` 

# Copyright and License

las-to-uv3 - Huriel Reichel Nils Hamel
Copyright (c) 2020 STDL, Swiss Territorial Data Lab

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY-NC-SA.
