<!--
 * @Date: 2021-03-19 15:52:32
 * @Author: David Pagnon
 * @LastEditors: David Pagnon
 * @LastEditTime: 2021-03-19 15:52:32
 * @FilePath: /Maya-Mocap/Readme.md
-->

# Maya Mocap

> **N.B.: This toolbox is not maintained anymore. You can switch to [Pose2Sim_Blender](https://github.com/davidpagnon/Pose2Sim_Blender) to get access to similar tools (and more).**

**[Maya Mocap](https://github.com/davidpagnon/Maya-Mocap)** is a collection of open-source tools for Motion Capture in Maya.

Tested on Maya 2018 (python 2) and on Maya 2022 (python 3). Not tested on Linux nor MacOS yet.


## Contents
1. [How to](#how-to)
2. [Camera toolbox](#camera-toolbox)
3. [Imports](#imports)
    1. [OBJ sequence import](#obj-sequence-import)
    2. [Opensim import](#opensim-import)
    3. [TRC import](#trc-import)
    4. [C3D import](#c3d-import)
    5. [BVH import](#bvh-import)
    6. [FBX import](#fbx-import)
4. [Others](#others)
    1. [C3D to TRC](#c3d-to-trc)
5. [To-do list](#to-do-list)
6. [Send Us Feedback!](#send-us-feedback)
9. [Contributers](#contributers)
10. [Citation](#citation)
11. [License](#license)

## How to

  1. First you need to install python packages in Maya.
  Open a command prompt (Windows -> cmd).\
  Type the following (replace `<YEAR>` with your version):
    
       ```
       "C:\Program Files\Autodesk\Maya<YEAR>\bin\mayapy" -m pip install opencv-python pandas c3d numpy anytree toml
       ```
&emsp;&emsp;If it does not work, check [there](http://mgland.com/qa/en/?qa=1748/how-to-use-pip-with-maya).
  
  2. Clone the repository or just download the python pieces of code you need.

  3. Open file at `<PATH_TO_DOCUMENTS_FOLDER>\maya\<YEAR>\maya.env`. Create it if it does't exist.\
     Type the following (replace what's in capital letters):
       ```
       MAYA_SHELF_PATH = <PATH_TO_MAYA_MOCAP>\shelves
       PYTHONPATH = <PATH_TO_MAYA_MOCAP>\scripts 
       MAYA_PLUG_IN_PATH = <PATH_TO_MAYA_MOCAP>\plug-ins
       ```
       
       You may also need to add this PYTHONPATH to your environment variables.\
       `Windows -> Environment Variables -> New -> Name: PYTHONPATH, Value: <PATH_TO_MAYA_MOCAP>\scripts` 
 
 
 That's it! After opening Maya, you should get a new shelf with new tools ready to be used.\
![image](https://user-images.githubusercontent.com/54667644/114212078-b3a8e580-9961-11eb-9b3c-6c69ffd114e3.png)


## Camera toolbox
`maya_camToolbox.py` is a toolbox for various operations on cameras in Maya.\
Lets you: 
* set cameras in scene from chosen specs.
* or set cameras from calibration file (.toml).
* save a calibration file from cameras in scene.
* film image sequences from the cameras in scene.
* display image sequences in scene.
* reproject selected objects on image camera planes.
* display 3D path of selected objects (due to a bug in Maya 2018, works only for "all frames" in this version).

![image](https://user-images.githubusercontent.com/54667644/113886128-b7e9cd00-97c0-11eb-99d5-35e6ceb51b7a.png)
![image](https://user-images.githubusercontent.com/54667644/113885480-28dcb500-97c0-11eb-85c4-cfa0edeee5ba.png)


## Imports

### OBJ sequence import
`maya_objs.py` lets you:
* Displays a sequence of OBJ files in an "objStreamNode" (uses plug-in `objStreamNode`).
* These OBJ don't need to be coherent in time (e.g. vertex number, etc).
* Assign textures to the meshes.

![image](https://user-images.githubusercontent.com/54667644/114210911-51031a00-9960-11eb-8320-d86390c3d4de.png)

### Opensim import
...Coming soon...\
`maya_osim.py` lets you:
* Import an .osim model.
* Animate it with .mot inverse kinematics.

### TRC import
`maya_trc.py` lets you:
* Import trc files.
* Choose if you only want to display the markers, or also to construct the skeleton.
* In case you want the skeleton (and it's not Openpose body_25b), please refer to the section SKELETON DEFINITION.

![image](https://user-images.githubusercontent.com/54667644/113013546-176e2a00-917c-11eb-977c-2cf9dc8513cb.png)

### C3D import
`maya_c3d.py` lets you:
* First convert c3d to trc files using `c3d2trc.py`.
* Then import resulting trc files.
* Choose if you only want to display the markers, or also to construct the skeleton.
* In case you want the skeleton (and it's not Openpose body_25b), please refer to SKELETON DEFINITION in trc import.
* :warning: Beware that it only allows you to retrieve 3D points, you won't get analog data with this code.

### BVH import
Jeroen Hoolmans wrote an awesome free [BVH (BioVision Hierarchy) importer](https://github.com/jhoolmans/mayaImporterBVH).\
It is slightly adapted here to be made compatibly with python 3 (Maya 2022 and above).

### FBX import
Instructions for importing FBX files can be found [at this address](https://www.instructables.com/How-To-Use-Mocap-Files-In-Maya-BVH-or-FBX/).


## Others
### C3D to TRC
`c3d2trc.py` lets you:
* Convert c3d binary files to trc format.
* Usage: Open a command line in your cloned repository. \
Type `python c3d2trc -i '<your_c3d_file>`
or `python c3d2trc.py -i <your_c3d_file> -o <your_trc_file>`.
* :warning: Beware that it only allows you to retrieve 3D points, you won't get analog data with this code.**

## To-do list
This repository is meant to get more tools in the future. Please feel free to add your suggestions and/or code!
Among others, I'd like to add:
- An Xsens importer.
- An Opensim importer (.osim model, and .mot inverse kinematics).


## Send Us Feedback!

This library is open source for research purposes, and I want to improve it! So let me know (create a new GitHub issue or pull request, email us, etc.) if you:
1. Find/fix any bug or know how to improve anything.
2. Want to add/show some cool functionality/demo/project regarding motion capture in Maya. We would love to integrate your project to this repository!

## Contributers
David Pagnon (maintainer), contact@david-pagnon.com\
Lionel Reveret, lionel.reveret@inria.fr

## Citation
If you find our work useful in your research, please cite it.
<!-- our paper [RFC] https://www.ye-yuan.com/rfc
```
@inproceedings{yuan2020residual,
  title={Residual Force Control for Agile Human Behavior Imitation and Extended Motion Synthesis},
  author={Yuan, Ye and Kitani, Kris},
  booktitle={Advances in Neural Information Processing Systems},
  year={2020}
}
``` -->

## License
The code found on this repository is free to use, edit, and redistribute under the BSD-3 licensing terms.
