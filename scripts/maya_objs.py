#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Import OBJ sequence                          ##
    ##################################################
    
    Displays a node streaming OBJ files with their textures.
    These OBJ don't need to have the same amount of vertices along time.
    Uses the plug-in objStreamNode.py
'''


## INIT
import maya.cmds as cmds
from maya_utils import *
import re

cmds.loadPlugin('objStreamNode')


## AUTHORSHIP INFORMATION
__author__ = "David Pagnon"
__copyright__ = "Copyright 2021, Maya-Mocap"
__credits__ = ["David Pagnon"]
__license__ = "BSD 3-Clause License"
__version__ = "1.0"
__maintainer__ = ["David Pagnon"]
__email__ = ["contact@david-pagnon.com"]
__status__ = "Production"


## FUNCTIONS
def obj_callback(*args):
    '''
    Inputs checkbox choice and obj folder path
    Creates objStreamNode
    Assigns texture if demanded
    '''
    filter = "Obj files (*.obj);; All Files (*.*)"
    obj_path = cmds.fileDialog2(fileFilter=filter, dialogStyle=2, cap="Choose the first OBJ file", fm=1)[0]
    obj_path_seq = re.sub(r'\.[0-9]+\.', '.%05d.', obj_path)
    obj_name = increment_name('OBJ')
    
    # Nodes creation and connections
    obj_transform = cmds.createNode('transform', name=obj_name)
    obj_shape = cmds.createNode('mesh', name=obj_transform+'Shape', parent=obj_transform)
    obj_streamNode = cmds.createNode('objStreamNode')
    cmds.setAttr(obj_streamNode+'.fname',obj_path_seq,type='string')
    cmds.connectAttr('time1.outTime', obj_streamNode+'.index')
    cmds.connectAttr(obj_streamNode+'.outMesh', obj_shape+'.inMesh')
    
    # Apply texture
    texture_check = cmds.checkBox(texture_box, query=True, value=True)
    if texture_check == True:
        filetype='png'
        img_dir = os.path.dirname(obj_path)
        # Change image names to comply with 'name.XXX.png'
        rename4seq(img_dir, filetype)
        # Apply texture
        img_files = glob.glob(os.path.join(img_dir, '*.'+filetype))
        applyTexture(obj_shape, img_files[0], sequence=True)
        

## WINDOW CREATION
def objs_window():
    '''
    Creates and displays window
    '''
    global texture_box
    
    window = cmds.window(title='Import OBJ sequence', width=300)
    cmds.columnLayout( adjustableColumn=True )
    texture_box = cmds.checkBox(label='Also import texture', value=True, ann='Import texture if provided')
    cmds.button(label='Import obj sequence', ann='Import and display obj sequence', command = obj_callback)
    cmds.showWindow(window)

if __name__ == "__main__":
    objs_window()