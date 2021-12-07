#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Maya Utils                                   ##
    ##################################################
    
    Small utility functinos for Maya-Mocap: 
    - increment name to deal with some collisions in Maya names attributions.
    - rename images to make Maya recognize them as a sequence.
    - apply texture to object.
'''


## INIT
import maya.cmds as cmds
import toml
import numpy as np
import cv2
import os
import glob
import sys
import re


## AUTHORSHIP INFORMATION
__author__ = "David Pagnon"
__copyright__ = "Copyright 2021, Maya-Mocap"
__credits__ = ["David Pagnon"]
__license__ = "BSD 3-Clause License"
__version__ = "0.1"
__maintainer__ = "David Pagnon"
__email__ = "contact@david-pagnon.com"
__status__ = "Development"


## FUNCTIONS
def increment_name(name):   
    '''
    Increment object names starting with str
    '''
    name = name.split('|')[-1]
    name_root = re.sub(r'[|0-9]', '', name)
    objs = cmds.ls('*'+name_root+'*', type='transform')
    objs = [obj.split('|')[-1] for obj in objs]
    cnt=1
    while name in objs:
        name_root = re.sub(r'[|0-9]', '', name)
        name = name_root+str(cnt)
        cnt+=1
        if cnt==100:
            break
    return name
    

def rename4seq(dir, filetype):
    '''
    Change names to comply with 'name.%3d.extension'
    Maya needs such names to identify files as a sequence.
    '''
    files = glob.glob(os.path.join(dir, '*.'+filetype))
    try: 
        int(os.path.basename(files[0]).split('.')[-2]) # verif .XXX.
        return
    except:
        # change name?
        confirm = cmds.confirmDialog(title='Confirm', message='Rename files to help Maya identify them as a sequence?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if confirm == 'No':
            return
        # change name.
        for i, f in enumerate(files):
            os.rename(f, os.path.join(dir, os.path.basename(dir)+ '.%05d.'%(i+1) + filetype))
        print(dir, ': Files renamed')

    
def applyTexture(shape, filename, sequence=False):
    '''
    Apply image (or image sequence) texture to shape.
    Inspired from https://stackoverflow.com/questions/15268511/maya-python-place-image-on-a-plane.
    '''
    shader = cmds.shadingNode('surfaceShader', asShader=True)
    SG = cmds.sets(empty=True, renderable=True, noSurfaceShader=True, name=shader+"SG")
    cmds.connectAttr(shader+'.outColor', SG+".surfaceShader", force=True)
    img = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(img+'.fileTextureName', filename, type='string')
    cmds.connectAttr(img+'.outColor', shader+'.outColor', force=True)
    
    cmds.sets(shape, edit=True, forceElement=SG)
    if sequence:
        ufe = cmds.setAttr(img+'.useFrameExtension', True)
        cmds.expression( s='{}.frameExtension=frame'.format(img) )


def retrieveCal(path):
    '''
    Retrieve calibration parameters from toml file.
    Output a dialog window to choose calibration file.
    '''
    S, D, K, R, T, P = {}, {}, {}, {}, {}, {}
    Kh, H = [], []
    cal = toml.load(path)
    cal_keys = [i for i in cal.keys() if 'metadata' not in i] # exclude metadata key
    for i, cam in enumerate(cal_keys):
        S[cam] = np.array(cal[cam]['size'])
        D[cam] = np.array(cal[cam]['distortions'])
        
        K[cam] = np.array(cal[cam]['matrix'])
        Kh = np.block([K[cam], np.zeros(3).reshape(3,1)])
        
        R[cam], _ = cv2.Rodrigues(np.array(cal[cam]['rotation']))
        T[cam] = np.array(cal[cam]['translation'])
        H = np.block([[R[cam],T[cam].reshape(3,1)], [np.zeros(3), 1 ]])
        
        P[cam] = Kh.dot(H)
        
    return S, D, K, R, T, P
