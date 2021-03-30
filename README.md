<!--
 * @Date: 2021-03-19 15:52:32
 * @Author: David Pagnon
 * @LastEditors: David Pagnon
 * @LastEditTime: 2021-03-19 15:52:32
 * @FilePath: /Maya-Mocap/Readme.md
-->

# Maya Mocap

**[Maya Mocap](https://github.com/davidpagnon/Maya-Mocap)** is a collection of open-source tools for Motion Capture in Maya.




## Contents
1. [How to](#how-to)
2. [Imports](#imports)
    1. [Opensim import](#opensim-import)
    2. [TRC import](#trc-import)
    3. [C3D import](#c3d-import)
    4. [BVH import](#bvh-import)
    5. [FBX import](#fbx-import)
5. [Camera toolbox](#camera-toolbox)
6. [To-do list](#to-do-list)
7. [Send Us Feedback!](#send-us-feedback)
8. [Contributers](#contributers)
9. [License](#license)

## How to

  1. First you need to install python packages in Maya.
  Open a command prompt (Windows -> cmd).\
  Type the following (beware of replacing <year> with your version):
    
       ```
       "C:\Program Files\Autodesk\Maya<year>\bin\mayapy" -m pip install pandas c3d numpy
       ```
&emsp;&emsp;If it does not work, check [there](http://mgland.com/qa/en/?qa=1748/how-to-use-pip-with-maya).
  
  2. Clone the repository or just download the python piece of code you need.

  3. Add each piece of code to your shelf as an executable button.\
Click on 'Create a new shelf', and then edit it by clicking on 'Shelf editor'.\
Under 'Command' tab, select 'Python', and type `execfile("PATH_TO_YOUR_SCRIPT.py")`.

![image](https://user-images.githubusercontent.com/54667644/111802309-1f051780-88ce-11eb-947d-7d88ae05b634.png)\
![image](https://user-images.githubusercontent.com/54667644/111801482-4a3b3700-88cd-11eb-8d47-952bc40f0106.png)

## Imports

### Opensim import
...Coming soon...
* Lets you import .osim model.
* Lets you animate it with .mot inverse kinematics.
* 
### TRC import
Lets you:
* Import trc files.
* Choose if you only want to display the markers, or also to construct the skeleton.
* In case you want the skeleton (and it's not Openpose body_25b), please refer to help on function "set_skeleton".

![image](https://user-images.githubusercontent.com/54667644/111803632-81124c80-88cf-11eb-8759-89e39774de7f.png)

### C3D import
Lets you:
* Convert c3d to trc.
* Import c3d files.
* Choose if you only want to display the markers, or also to construct the skeleton.
* In case you want the skeleton (and it's not Openpose body_25b), please refer to help on function "set_skeleton".
* :warning: Beware that it only allows you to retrieve 3D points, you won't get analog data with this code.

### BVH import
A free BVH (BioVision Hierarchy) importer by Jeroen Hoolmans can be found [on this repo](https://github.com/jhoolmans/mayaImporterBVH)

## FBX import
Instructions for importing FBX files can be found [at this address](https://www.instructables.com/How-To-Use-Mocap-Files-In-Maya-BVH-or-FBX/).

## Camera toolbox
A toolbox for various operations on cameras in Maya.\
Lets you: 
* set cameras in scene from chosen specs.
* or set cameras from calibration file (.toml).
* save a calibration file from cameras in scene.
* film image sequences from the cameras in scene.
* display films in scene.

![image](https://user-images.githubusercontent.com/54667644/111811597-84113b00-88d7-11eb-803f-1b9726523793.png)


## To-do list
This repository is meant to get more tools in the future. Please feel free to add your suggestions and/or code!
Among others, I'd like to add:
- An Xsens importer
- An Opensim importer (.osim model, and .mot inverse kinematics)
- A code for importing one mesh per frame on GPU nodes


## Send Us Feedback!

This library is open source for research purposes, and I want to improve it! So let me know (create a new GitHub issue or pull request, email us, etc.) if you:
1. Find/fix any bug or know how to improve anything.
2. Want to add/show some cool functionality/demo/project regarding motion capture in Maya. We would love to integrate your project to this repository!

## Contributers
David Pagnon (maintainer), contact@david-pagnon.com\
Lionel Reveret, lionel.reveret@inria.fr\
Thibault Goyallon, thibault.goyallon@inria.fr

## License
The code found on this repository is free to use, edit, and redistribute under the BSD-3 licensing terms.
