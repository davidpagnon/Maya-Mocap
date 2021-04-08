#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Convert c3d files to trc and import them     ##
    ##################################################
    
    Choose if you only want to display the markers, or also to construct the skeleton.
    In case you want the skeleton, please refer to help on function "set_skeleton".
    Beware that it only allows you to retrieve 3D points, you won't get analog data from this code. 
'''


## INIT
import c3d2trc
import maya_trc


## AUTHORSHIP INFORMATION
__author__ = "David Pagnon"
__copyright__ = "Copyright 2021, Maya-Mocap"
__credits__ = ["David Pagnon"]
__license__ = "BSD 3-Clause License"
__version__ = "1.0"
__maintainer__ = "David Pagnon"
__email__ = "contact@david-pagnon.com"
__status__ = "Production"


## FUNCTIONS
def c3d_callback(*arg):
    '''
    Inputs checkbox choices and trc path
    Converts c3d to trc
    Reads trc file
    Set markers and skeleon in scene
    '''
    filter = "C3D files (*.c3d);; All Files (*.*)"
    c3d_path = cmds.fileDialog2(fileFilter=filter, dialogStyle=2, cap="Open File", fm=1)[0]
    
    c3d2trc(c3d_path)
    trc_path = c3d_path.replace('.c3d', '.trc')
    
    _, data = df_from_trc(trc_path)
    labels, str_cnt, numFrames = analyze_data(data)
    cmds.group(empty=True, name='C3D'+str_cnt)
    
    markers_check = cmds.checkBox(markers_box, query=True, value=True)
    if markers_check == True:
        set_markers(data, labels, numFrames)
        cmds.group(cmds.ls(labels), n='markers'+str_cnt)
        cmds.parent('markers'+str_cnt, 'C3D'+str_cnt)

    skeleton_check = cmds.checkBox(skeleton_box, query=True, value=True)
    if skeleton_check == True:
        set_skeleton(data, str_cnt, numFrames)
        cmds.parent(root+str_cnt, 'C3D'+str_cnt)
        
    cmds.playbackOptions(minTime=0, maxTime=numFrames)
    cmds.playbackOptions(playbackSpeed = 1)


## WINDOW CREATION
window = cmds.window(title='Import C3D', width=300)
cmds.columnLayout( adjustableColumn=True )
markers_box = cmds.checkBox(label='Display markers', ann='Display markers as locators')
skeleton_box = cmds.checkBox(label='Display skeleton', ann='Reconstruct skeleton. Needs to be Openpose body_25b, or else you need to adapt your hierarchy in function.')
cmds.button(label='Import c3d', ann='Import and display c3d', command = c3d_callback)
cmds.showWindow(window)