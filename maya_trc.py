'''
Import trc files.
Choose if you want only the markers, or also to construct the skeleton.
In case you want the skeleton, please refer to help on function "set_skeleton".
'''


## INIT
import maya.cmds as cmds
import numpy as np
import pandas as pd


## FUNCTIONS
def df_from_trc(trc_path):
    '''
    Retrieve header and data from trc
    '''
    df_header = pd.read_csv(trc_path, sep="\t", skiprows=1, header=None, nrows=2)
    header = dict(zip(df_header.iloc[0].tolist(), df_header.iloc[1].tolist()))
    
    df_lab = pd.read_csv(trc_path, sep="\t", skiprows=3, nrows=1)
    labels = df_lab.columns.tolist()[2:-1:3]
    labels_XYZ = np.array([[labels[i]+'_X', labels[i]+'_Y', labels[i]+'_Z'] for i in range(len(labels))], dtype='object').flatten()
    labels_FTXYZ = np.concatenate((['Frame#','Time'], labels_XYZ))
    
    data_df = pd.read_csv(trc_path, sep="\t", skiprows=5, index_col=False, header=None, names=labels_FTXYZ)
    data = data_df.iloc[:,2:] # Remove columns 'Frame#' and 'Time'
    
    return header, data
   

def increment_labels(labels):
    '''
    Increment label names in case of previous trc importations
    '''
    objs = cmds.ls(type='transform')
    cnt=1 
    for l in labels:
        if l+str(cnt) in objs:
            cnt+=1
            continue
    str_cnt = str(cnt)
    labels_cnt = [l+str_cnt for l in labels]
    
    return str_cnt, labels_cnt
    

def analyze_data(data):
    '''
    Get frame number, labels, and increment in case of previous imports
    '''
    numFrames = data.shape[0]
    labels_raw = data.columns
    labels = [labels_raw[2::3][i][:-2] for i in range(len(labels_raw[2::3]))]

    str_cnt, labels = increment_labels(labels)
    
    return labels, str_cnt, numFrames

    
def set_markers(data, labels, numFrames):
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
    for i in range(numFrames):
        for j in range(len(labels)):
            cmds.setKeyframe(labels[j], t=i, at='translateX', v=data.iloc[i,3*j+2])
            cmds.setKeyframe(labels[j], t=i, at='translateY', v=data.iloc[i,3*j])
            cmds.setKeyframe(labels[j], t=i, at='translateZ', v=data.iloc[i,3*j+1])
    

def set_skeleton(data, str_cnt, numFrames):
    '''
    Set skeleton from trc
    
    This is given for the OpenPose body_25b joint hierarchy.
    You need to adapt it to the hierarchy of your own skeleton model.
    1. Your joint names should be your trc labels + letter J.
       Example : trc label = 'CHip' --> joint name = 'CHipJ'
    2. Then you need to make sure your skeleton hierarchy is respected.
       Your joint names must be defined from the root one to the more distal ones.
       
    /!\ Be sure to set Evaluation mode to DG /!\
    Windows -> Settings/Preferences -> Preferences -> Animation -> Evaluation mode -> DG
    It may help your bones connect your joints
    '''
        
    # Create joints
    cmds.select(deselect=True)
    # Hip center (CHipJ) is needed as a root joint, although it's not given by body_25b model.
    # We will define it further down as the midpoint between the right and the left joint.
    cmds.joint(name='CHipJ'+str_cnt)

    cmds.joint(name='RHipJ'+str_cnt)
    cmds.joint(name='RKneeJ'+str_cnt)
    cmds.joint(name='RAnkleJ'+str_cnt)
    cmds.joint(name='RBigToeJ'+str_cnt)
    cmds.joint(name='RSmallToeJ'+str_cnt)
    cmds.select('RAnkleJ'+str_cnt)
    cmds.joint(name='RHeelJ'+str_cnt)

    cmds.select('CHipJ'+str_cnt)
    cmds.joint(name='LHipJ'+str_cnt)
    cmds.joint(name='LKneeJ'+str_cnt)
    cmds.joint(name='LAnkleJ'+str_cnt)
    cmds.joint(name='LBigToeJ'+str_cnt)
    cmds.joint(name='LSmallToeJ'+str_cnt)
    cmds.select('LAnkleJ'+str_cnt)
    cmds.joint(name='LHeelJ'+str_cnt)

    cmds.select('CHipJ'+str_cnt)
    cmds.joint(name='NeckJ'+str_cnt)
    cmds.joint(name='HeadJ'+str_cnt)
    cmds.joint(name='NoseJ'+str_cnt)

    cmds.select('NeckJ'+str_cnt)
    cmds.joint(name='RShoulderJ'+str_cnt)
    cmds.joint(name='RElbowJ'+str_cnt)
    cmds.joint(name='RWristJ'+str_cnt)

    cmds.select('NeckJ'+str_cnt)
    cmds.joint(name='LShoulderJ'+str_cnt)
    cmds.joint(name='LElbowJ'+str_cnt)
    cmds.joint(name='LWristJ'+str_cnt)

    cmds.select('CHipJ'+str_cnt, hi=True)
    jointsJ = cmds.ls(sl=1)
    
    for j in range(1,len(jointsJ)):
        cmds.joint(cmds.listRelatives(jointsJ[j], parent=True), e=True, zso=True, oj='xyz', sao='yup')
        
    # Place joints
    for i in range(numFrames):
        for j in range(len(jointsJ)):
            if j == 0: #CHipJ
                jointCoordX = np.add(data.loc[i,'LHip_Z'], data.loc[i,'RHip_Z']) / 2
                jointCoordY = np.add(data.loc[i,'LHip_X'], data.loc[i,'RHip_X']) / 2
                jointCoordZ = np.add(data.loc[i,'LHip_Y'], data.loc[i,'RHip_Y']) / 2
            else:
                jointCoordX = data.loc[i,jointsJ[j][:-2]+'_Z']
                jointCoordY = data.loc[i,jointsJ[j][:-2]+'_X']
                jointCoordZ = data.loc[i,jointsJ[j][:-2]+'_Y']
                
            cmds.move(jointCoordX, jointCoordY, jointCoordZ, jointsJ[j], a=True)
            cmds.setKeyframe(jointsJ[j], t=i)


def trc_callback(*arg):
    '''
    Inputs checkbox choices and trc path
    Reads trc file
    Set markers and skeleon in scene
    '''
    filter = "Trc files (*.trc);; All Files (*.*)"
    trc_path = cmds.fileDialog2(fileFilter=filter, dialogStyle=2, cap="Open File", fm=1)[0]
    
    _, data = df_from_trc(trc_path)
    labels, str_cnt, numFrames = analyze_data(data)
    cmds.group(empty=True, name='TRC'+str_cnt)
    
    markers_check = cmds.checkBox(markers_box, query=True, value=True)
    if markers_check == True:
        set_markers(data, labels, numFrames)
        cmds.group(cmds.ls(labels), n='markers'+str_cnt)
        cmds.parent('markers'+str_cnt, 'TRC'+str_cnt)

    skeleton_check = cmds.checkBox(skeleton_box, query=True, value=True)
    if skeleton_check == True:
        set_skeleton(data, str_cnt, numFrames)
        cmds.parent('CHipJ'+str_cnt, 'TRC'+str_cnt)
        
    cmds.playbackOptions(minTime=0, maxTime=numFrames)
    cmds.playbackOptions(playbackSpeed = 1)
    
   
## WINDOW CREATION
window = cmds.window(title='Import TRC', width=300)
cmds.columnLayout( adjustableColumn=True )
markers_box = cmds.checkBox(label='Display markers', ann='Display markers as locators')
skeleton_box = cmds.checkBox(label='Display skeleton', ann='Reconstruct skeleton. Needs to be Openpose body_25b, or else you need to adapt your hierarchy in function.')
cmds.button(label='Import trc', ann='Import and display trc', command = trc_callback)
cmds.showWindow(window)

