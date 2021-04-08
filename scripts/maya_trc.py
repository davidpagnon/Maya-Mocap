#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Import trc files                             ##
    ##################################################
    
    Choose if you only want to display the markers, or also to construct the skeleton.
    In case you want the skeleton, please refer to help on function "set_skeleton".
'''


## INIT
import maya.cmds as cmds
import numpy as np
import pandas as pd
import re
from anytree import Node, RenderTree


## AUTHORSHIP INFORMATION
__author__ = "David Pagnon"
__copyright__ = "Copyright 2021, Maya-Mocap"
__credits__ = ["David Pagnon"]
__license__ = "BSD 3-Clause License"
__version__ = "1.0"
__maintainer__ = "David Pagnon"
__email__ = "contact@david-pagnon.com"
__status__ = "Production"


## SKELETON DEFINITION
'''
This is given for the OpenPose body_25b joint hierarchy.
Not taken into account if you're only importing the markers.

If you want to import the skeleton, you need to adapt it to your own skeleton hierarchy.
1. Your joint names should be your trc labels + letter J.
   Example : trc label = 'CHip' --> joint name = 'CHipJ'
2. Then you need to make sure your skeleton hierarchy is respected.
   Your joint names must be defined from the root one to the more distal ones.
3. Finally, reload the module: 
  `from imp import reload
   reload maya_trc`
'''
root = Node("CHipJ", children=[
    Node("RHipJ", children=[
        Node("RKneeJ", children=[
            Node("RAnkleJ", children=[
                Node("RBigToeJ", children=[
                    Node("RSmallToeJ"),
                ]),
                Node("RHeelJ"),
            ]),
        ]),
    ]),
    Node("LHipJ", children=[
        Node("LKneeJ", children=[
            Node("LAnkleJ", children=[
                Node("LBigToeJ", children=[
                    Node("LSmallToeJ"),
                ]),
                Node("LHeelJ"),
            ]),
        ]),
    ]),
    Node("NeckJ", children=[
        Node("HeadJ", children=[
            Node("NoseJ"),
        ]),
        Node("RShoulderJ", children=[
            Node("RElbowJ", children=[
                Node("RWristJ"),
            ]),
        ]),
        Node("LShoulderJ", children=[
            Node("LElbowJ", children=[
                Node("LWristJ"),
            ]),
        ]),
    ]),
])


## FUNCTIONS
def df_from_trc(trc_path):
    '''
    Retrieve header and data from trc
    '''
    # DataRate	CameraRate	NumFrames	NumMarkers	Units	OrigDataRate	OrigDataStartFrame	OrigNumFrames
    df_header = pd.read_csv(trc_path, sep="\t", skiprows=1, header=None, nrows=2, encoding="ISO-8859-1")
    header = dict(zip(df_header.iloc[0].tolist(), df_header.iloc[1].tolist()))
    
    # Label1_X  Label1_Y    Label1_Z    Label2_X    Label2_Y
    df_lab = pd.read_csv(trc_path, sep="\t", skiprows=3, nrows=1)
    labels = df_lab.columns.tolist()[2:-1:3]
    labels_XYZ = np.array([[labels[i]+'_X', labels[i]+'_Y', labels[i]+'_Z'] for i in range(len(labels))], dtype='object').flatten()
    labels_FTXYZ = np.concatenate((['Frame#','Time'], labels_XYZ))
    
    data = pd.read_csv(trc_path, sep="\t", skiprows=5, index_col=False, header=None, names=labels_FTXYZ)
    
    return header, data
    
    
def increment_labels(labels):
    '''
    Increment label names in case of previous trc importations
    '''
    objs = cmds.ls(type='transform')
    cnt=1 
    for l in labels:
        if l+str(cnt) in objs or l+'J'+str(cnt) in objs:
            cnt+=1
            continue
    str_cnt = str(cnt)
    labels_cnt = [l+str_cnt for l in labels]
    
    return str_cnt, labels_cnt
    

def analyze_data(data):
    '''
    Get frame number, labels, and increment in case of previous imports
    '''
    rangeFrames = range(data['Frame#'].iloc[0], data['Frame#'].iloc[-1]+1)
    labels_raw = data.columns
    labels = [labels_raw[2::3][i][:-2] for i in range(len(labels_raw[2::3]))]
    str_cnt, labels = increment_labels(labels)
    
    return labels, str_cnt, rangeFrames

    
def set_markers(data, labels, rangeFrames):
    '''
    Set markers from trc
    '''
    
    # Create markers
    for j in range(len(labels)):
        if j==0:
            cmds.polySphere(r=.03, sx=20, sy=20, n=labels[j])
        else:
            cmds.instance(labels[0], n=labels[j])
    # Place markers
    firstFrame = rangeFrames[0]
    for i in rangeFrames:
        for j in range(len(labels)):
            cmds.setKeyframe(labels[j], t=i, at='translateX', v=data.iloc[i-firstFrame,3*j+2 +2])
            cmds.setKeyframe(labels[j], t=i, at='translateY', v=data.iloc[i-firstFrame,3*j +2])
            cmds.setKeyframe(labels[j], t=i, at='translateZ', v=data.iloc[i-firstFrame,3*j+1 +2])

            
def print_skeleton():
    '''
    Prints skeleton.
    '''
    for pre, _, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

        
def set_skeleton(data, str_cnt, rangeFrames):
    '''
    Set skeleton from trc
    In case you're not using the model body_25b from openpose, you need to modify the section SKELETON DEFINITION
    If bones are not connecting the joints, uncomment the last line of the function (evaluation manager mode ON)
    '''
    # Create joints
    cmds.select(None)
    cmds.joint(name = root.name+str_cnt)
    for _, _, node in RenderTree(root):    
        if node.name != root.name:
            cmds.select(node.parent.name+str_cnt)
            cmds.joint(name = node.name+str_cnt)
    cmds.select('CHipJ'+str_cnt, hi=True)
    jointsJ = cmds.ls(sl=1)
    
    # Place and orient joints
    firstFrame = rangeFrames[0]
    for i in rangeFrames:
        for j in range(len(jointsJ)): # place joints
            if j == 0 and not root.name[:-1] in data.columns: #If model has no root, take midpoint of hips
                RHip, LHip = root.children[0].name[:-1], root.children[1].name[:-1]
                jointCoordX = np.add(data.loc[i-firstFrame,RHip+'_Z'], data.loc[i-firstFrame,LHip+'_Z']) / 2
                jointCoordY = np.add(data.loc[i-firstFrame,RHip+'_X'], data.loc[i-firstFrame,LHip+'_X']) / 2
                jointCoordZ = np.add(data.loc[i-firstFrame,RHip+'_Y'], data.loc[i-firstFrame,LHip+'_Y']) / 2
            else:
                jnt =  re.sub(r'[0-9]', '', jointsJ[j])[:-1] # take off numbers + letter J from joint name
                jointCoordX = data.loc[i-firstFrame,jnt+'_Z']
                jointCoordY = data.loc[i-firstFrame,jnt+'_X']
                jointCoordZ = data.loc[i-firstFrame,jnt+'_Y']
            cmds.move(jointCoordX, jointCoordY, jointCoordZ, jointsJ[j], a=True)
            cmds.setKeyframe(jointsJ[j], t=i)
        if i == firstFrame:  # orient joints
            for j in range(1,len(jointsJ)):
                cmds.joint(cmds.listRelatives(jointsJ[j], parent=True), e=True, zso=True, oj='xyz', sao='yup')
                cmds.setKeyframe(jointsJ[j], t=i)

    '''Evaluation mode to DG to make sure bones are connecting the joints
    Change it in Windows -> Settings/Preferences -> Preferences -> Animation -> Evaluation mode -> DG'''
    # cmds.evaluationManager(mode="off")

def trc_callback(*arg):
    '''
    Inputs checkbox choices and trc path
    Reads trc file
    Set markers and skeleon in scene
    '''
    filter = "Trc files (*.trc);; All Files (*.*)"
    trc_path = cmds.fileDialog2(fileFilter=filter, dialogStyle=2, cap="Open File", fm=1)[0]
    
    _, data = df_from_trc(trc_path)
    labels, str_cnt, rangeFrames = analyze_data(data)
    cmds.group(empty=True, name='TRC'+str_cnt)
    
    markers_check = cmds.checkBox(markers_box, query=True, value=True)
    if markers_check == True:
        set_markers(data, labels, rangeFrames)
        cmds.group(cmds.ls(labels), n='markers'+str_cnt)
        cmds.parent('markers'+str_cnt, 'TRC'+str_cnt)

    skeleton_check = cmds.checkBox(skeleton_box, query=True, value=True)
    if skeleton_check == True:
        print_skeleton()
        set_skeleton(data, str_cnt, rangeFrames)
        cmds.parent(root.name+str_cnt, 'TRC'+str_cnt)
        
    cmds.playbackOptions(minTime=rangeFrames[0], maxTime=rangeFrames[-1])
    cmds.playbackOptions(playbackSpeed = 1)
    
   
## WINDOW CREATION
def trc_window():
    global markers_box
    global skeleton_box
    
    window = cmds.window(title='Import TRC', width=300)
    cmds.columnLayout( adjustableColumn=True )
    markers_box = cmds.checkBox(label='Display markers', ann='Display markers as locators')
    skeleton_box = cmds.checkBox(label='Display skeleton', ann='Reconstruct skeleton. Needs to be Openpose body_25b, or else you need to adapt your hierarchy in function.')
    cmds.button(label='Import trc', ann='Import and display trc', command = trc_callback)
    cmds.showWindow(window)

if __name__ == "__main__":
    trc_window()