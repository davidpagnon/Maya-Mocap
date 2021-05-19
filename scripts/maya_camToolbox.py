#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Camera toolbox                               ##
    ##################################################
    
    Lets you: 
    - set cameras in scene from chosen specs.
    - or set cameras from calibration file (.toml).
    - save a calibration file from cameras in scene.
    - film image sequences from the cameras in scene.
    - display films in scene.
'''


## INIT
import maya.cmds as cmds
import os
import glob
import numpy as np
import cv2
import maya_utils


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
def textOff(*args):
    '''
    Disable textFields if radioButton checked
    '''
    if cmds.radioButton(allFrames_box, query=True, select=True):
        cmds.textField(pre_field, edit=True, enable=False)
        cmds.textField(post_field, edit=True, enable=False)
    else:
        cmds.textField(pre_field, edit=True, enable=True)
        cmds.textField(post_field, edit=True, enable=True)
        
        
def setCamsfromSpecs_callback(*args):
    '''
    Set cameras from specs.
    Prompts a set of custom specs, and creates cameras.
    Another possibility would be to set cameras at the center of polyPlatonicSolid (not implemeted).
    '''
    # retrieve specs
    number = int(cmds.textFieldGrp(number_field, query=1, text=1))
    distance = float(cmds.textFieldGrp(distance_field, query=1, text=1))
    fm = float(cmds.textFieldGrp(focal_field, query=1, text=1))
    W = float(cmds.textFieldGrp(width_field, query=1, text=1))
    H = float(cmds.textFieldGrp(height_field, query=1, text=1))
    disto = float(cmds.textFieldGrp(disto_field, query=1, text=1))
    px_size = float(cmds.textFieldGrp(pxsize_field, query=1, text=1)) * 1e-6
    binning_factor = float(cmds.textFieldGrp(binning_field, query=1, text=1))

    cmds.setAttr("defaultResolution.width", W/binning_factor) 
    cmds.setAttr("defaultResolution.height", H/binning_factor) 
    
    # set cameras
    cams = []
    for c in range(number):
        cam, camShape = cmds.camera(n='cam_%d'%(c+1), focalLength=fm, horizontalFilmAperture = W*px_size*39.3701, verticalFilmAperture = H*px_size*39.3701) # m->inch : *39.3701
        cams.append(cam)
        cmds.setAttr(camShape + '.aiRadialDistortion', disto) #1 for GoPro (roughly)
        if number == 2 or number == 4:
            ang = 90*c * np.pi/180
            cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1])
        elif number == 8:
            ang = 45*c * np.pi/180
            cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1])
        elif number == 16:
            if c<8:
                ang = 45*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1.5])
            else:
                ang = 22.5 + 45*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), .5])
        elif number == 32:
            if c<16:
                ang = 22.5*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1.5])
            elif c<24:
                ang = -11.25 + 45*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), .5])
            elif c<32:
                ang = 11.25 + 45*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 2.5])
        elif number == 64:
            if c<32:
                ang = 11.25*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1.5])
            elif c<48:
                ang = 11.25 + 22.5*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), .5])
            elif c<64:
                ang = 11.25 + 22.5*c * np.pi/180
                cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 2.5])
                
        cmds.viewPlace(camShape, lookAt=(0, 0, 1))
       
    cmds.select(cams)
    cmds.group(n='cameras')

    
def setCamsfromCal_callback(*args):
    '''
    Set cameras from calibration file.
    Create cameras according to the calibration file chosen from dialog window.
    '''
    px_size = float(cmds.textFieldGrp(pxsize_field, query=1, text=1)) * 1e-6
    binning_factor = float(cmds.textFieldGrp(binning_field, query=1, text=1))
    
    # open file dialog (fm = 0 pour sauver plutot qu'ouvrir)
    singleFilter = "Toml calibration files (*.toml)"
    path = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Open Calibration File", fm=1)[0]
    # retrieve calibration
    S, D, K, R, T, P = maya_utils.retrieveCal(path)
    
    # set cameras
    cams=[]
    for c in range(len(R)): # Pour chaque cam
        Rc =  R['cam_%d' %(c+1)].T
        Tc = -R['cam_%d' %(c+1)].T . dot(T['cam_%d' %(c+1)])# / 1000 # Pour l'avoir en m
        M = np.block([[Rc,Tc.reshape(3,1)], [np.zeros(3), 1 ]])
        Mlist = M.T.reshape(1,-1)[0].tolist()
        
        fm = K['cam_%d' %(c+1)][0, 0] * px_size * 1000 # fp*px*1000 [mm]
        
        W, H = S['cam_%d' %(c+1)]        
        
        cam, camShape = cmds.camera(n='cam_%d' %(c+1), focalLength=fm, horizontalFilmAperture = W*px_size*39.3701*binning_factor, verticalFilmAperture = H*px_size*39.3701*binning_factor)  # m->inch : *39.3701
        cams.append(cam) 

        cmds.setAttr(camShape + '.aiRadialDistortion', float(-D['cam_%d' %(c+1)][0]*4)) # Cuisine pour passer de la distorsion de maya (fisheye?) a celle de opencv (pinhole?)
        cmds.xform(cam, m=Mlist)
        cmds.setAttr("defaultResolution.width", W) 
        cmds.setAttr("defaultResolution.height", H) 
        cmds.select(cam)
        cmds.rotate(180,0,0, objectSpace=1, relative=1)

    cmds.select(cams)
    cmds.group(n='cameras')

    
def saveCalfromCam_callback(*args):
    '''
    Save calibration as a .toml file from cameras in scene.
    '''
    px_size = float(cmds.textFieldGrp(pxsize_field, query=1, text=1)) * 1e-6
    binning_factor = float(cmds.textFieldGrp(binning_field, query=1, text=1))
    
    sel = cmds.ls('cameras', dag=1)
    # Names
    cams = cmds.listRelatives(sel, type='transform')
    # Size
    W = cmds.camera(cams[0], q=1, horizontalFilmAperture=True) / (px_size*39.3701) / binning_factor
    H = cmds.camera(cams[0], q=1, verticalFilmAperture=True) / (px_size*39.3701) / binning_factor
    size = [W, H,]
    # Intrinsic parameters
    fm = cmds.camera(cams[0], q=1, focalLength=True)
    fp = fm *1e-3 / px_size
    cu, cv = W/2, H/2
    matrix = [[fp/binning_factor, 0., cu/binning_factor,], [0.0, fp/binning_factor, cv/binning_factor,], [0.0, 0.0, 1.0,],]
    # Distortion
    disto = cmds.getAttr(cams[0] + 'Shape1.aiRadialDistortion')
    distortions = [-disto/4, 0. ,0. ,0.,] # Cuisine pour passer de la distorsion de maya (fisheye?) a celle de opencv (pinhole?)
    # Rotation, Translation
    rotation, translation = [], []
    for c in range(len(cams)):
        Mlist = np.array( cmds.xform(cams[c], query=True, m=True) )
        Mmat = np.array(Mlist).reshape(4,4).T
        Rmat = np.array(Mmat).reshape(4,4)[:3,:3]
        Rmat = Rmat . dot(np.array([[1,0,0],[0,-1,0],[0,0,-1]])) # rotx 180
        Tmat = np.array(Mmat).reshape(4,4)[:3,3]
        
        rotation.append(cv2.Rodrigues(Rmat.T)[0] .flatten()  .tolist())
        translation.append( (-Rmat.T . dot(Tmat) ) .flatten() .tolist() ) # * 1000) . tolist() )

    # Save calibration as .toml file
    cal_folder = cmds.fileDialog2(dialogStyle=2, cap="Select folder to save calibration", fm=3)[0]
    with open(os.path.join(cal_folder, '%d_virtualCams_calibration.toml'%len(cams)), 'w+') as cal_f:
        for c in range(len(cams)):
            cam_str='[cam_%d]\n'%(c+1)
            name_str = 'name = "cam_%d"\n'%(c+1)
            size_str = 'size = ' + str(size) + '\n'
            mat_str = 'matrix = ' + str(matrix) + '\n'
            dist_str = 'distortions = ' + str(distortions) + '\n' 
            rot_str = 'rotation = ' + str(rotation[c]) + '\n'
            tran_str = 'translation = ' + str(translation[c]) + '\n'
            fish_str = 'fisheye = false\n\n'
            cal_f.write(cam_str + name_str + size_str + mat_str + dist_str + rot_str + tran_str + fish_str)
        meta = '[metadata]\nadjusted = false\nerror = 0.0\n'
        cal_f.write(meta)

        
def filmfromCam_callback(*args):
    '''
    Film playblast image sequences from each cameras in scene.
    '''
    # list cameras
    cameras = cmds.ls(type=('camera'), l=True)
    startup_cameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
    non_startup_cameras = [cam for cam in cameras if cam not in startup_cameras] 
    cam_transforms = list(map(lambda x: cmds.listRelatives(x, parent=True)[0], non_startup_cameras))
    
    # path and confirm dialog window
    path = cmds.fileDialog2(dialogStyle=2, cap="Choose video saving folder", fm=3)[0] # eg: G:\Op2Ani\191209_6miqus_xsens\dance_2\seq003
    videos_dir = os.path.join(path, '%d_cams_maya'%len(cam_transforms))
    if not os.path.exists(videos_dir): 
        os.mkdir(videos_dir) 
    else:
        confirm = cmds.confirmDialog( title='Confirm', message='Do you want to overwrite the folder?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if confirm == 'No':
            return
    
    # video specs
    size = cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")
    cmds.setAttr("defaultRenderGlobals.imageFormat", 32) # *.png
    cmds.grid(toggle=0)
    cmds.setAttr('cameras.visibility', 0)

    # film
    for i, c in enumerate(cam_transforms):
        cam_dir = os.path.join(videos_dir, os.path.basename(path)+'_cam%d_img'%(i+1))
        if not os.path.exists(videos_dir): os.mkdir(videos_dir) 

        cmds.select(c)
        cmds.lookThru(c)
        cmds.playblast(format='image', wh=size, percent=100, f=os.path.join(cam_dir,os.path.basename(path)+'_cam%d'%(i+1)), viewer=False)
    
    cmds.grid(toggle=1)
    cmds.setAttr('cameras.visibility', 1)
    cmds.lookThru('persp')

    
def setVidfromSeq_callback(*args):
    '''
    Display image sequences behind each camera in scene.
    Each sequence should be in a different camera folder which name includes 'img'.
    '''
    binning_factor = float(cmds.textFieldGrp(binning_field, query=1, text=1))
    filetype = cmds.textField(extension_field, query=1, text=1)
    scaling_check = cmds.checkBox(scaling_box, query=True, value=True)
    
    path = cmds.fileDialog2(dialogStyle=2, cap="Choose root directory of videos folders", fm=3)[0]
    img_dirs = list(filter( lambda item: 'img' in item, next(os.walk(path))[1] ))
    img_dirs_full = [os.path.join( path, dir ) for dir in img_dirs]
    
    # Change image names to comply with 'name.XXX.png'
    for img_dir in img_dirs_full:
        maya_utils.rename4seq(img_dir, filetype)
    img_files_per_cam = [glob.glob(os.path.join(dir,"*."+filetype)) for dir in img_dirs_full]
    
    # Set videos in scene
    cam_transforms = cmds.listRelatives(cmds.ls('cameras*')[0])
    nb_cam = len(cam_transforms)
    vidPlane = []
    for i, c in enumerate(cam_transforms): 
        # camera parameters
        fm = cmds.camera(c, query=True, focalLength=True)        
        camMat = cmds.xform(c, query=True, matrix=True)
        distance = cmds.xform(c, q=1, os=1, translation=1)[2]
        # image plane size at camera origin (m)
        W = cmds.camera(c, query=True, horizontalFilmAperture=True) / 39.3701 / binning_factor
        H = cmds.camera(c, query=True, verticalFilmAperture=True) / 39.3701 / binning_factor
        # create image plane
        vidPlane.append(maya_utils.increment_name('vid_%d' %(i+1)))
        vidPlane[i] = cmds.polyPlane(n=vidPlane[i], ax=[0,0,1], w=W, h=H)[0] 
        # set plane at camera locations
        cmds.xform(vidPlane[i], m=camMat)
        cmds.parent(vidPlane[i], c, absolute=True)
        
        if scaling_check == True: 
            # scale up and down while translating image plane
            cmds.expression(string = vidPlane[i]+'.scaleX' + '= -' + vidPlane[i]+'.translateZ' + '/ (' + str(fm) + '*1e-3)')
            cmds.expression(string = vidPlane[i]+'.scaleY' + '= -' + vidPlane[i]+'.translateZ' + '/ (' + str(fm) + '*1e-3)')
            # set plane one meter away from the camera plane
            cmds.setAttr(vidPlane[i]+'.translateZ',  -.5*distance)
        else:
            # scale plane to the size it would be at world origin
            cmds.setAttr(vidPlane[i]+'.scaleX',  distance/(fm*1e-3) )   # D/fm
            cmds.setAttr(vidPlane[i]+'.scaleY', distance/(fm*1e-3) )

    # Apply img texture to plane
        maya_utils.applyTexture(vidPlane[i], img_files_per_cam[i][0], sequence=True)

    panels = cmds.getPanel(type='modelPanel')
    [cmds.modelEditor(pan, e=1, displayTextures=1) for pan in panels]
    
    # Move tool axis orientation: along rotation axis in order to prevent weird translations
    cmds.manipPivot(mto=4)
    cmds.select(None)
    
    
def reproj_3D(*args):
    '''
    Reprojects 3D point to cameras in real time.
    Works only if you have cameras in scene.
    Looks best if you display videos with parameter "Apply scaling" on.
    '''
    # Cameras list
    cameras = cmds.ls(type=('camera'), l=True)
    startup_cameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
    non_startup_cameras = list(set(cameras) - set(startup_cameras))
    cam_transforms = list(map(lambda x: cmds.listRelatives(x, parent=True)[0], non_startup_cameras))
    pts_cams_coord = [cmds.xform(c, q=1, t=1) for c in cam_transforms]
    
    # 3D points list
    pt_3d_names = cmds.ls(sl=True)
    for p in range(len(pt_3d_names)):
        pt_3d_coord = cmds.xform(pt_3d_names[p], q=1, t=1, ws=1)
        curve_name_group = 'proj'+pt_3d_names[p]
        
        curve_name_cam = []
        for i, c in enumerate(cam_transforms):
            # Curve definition
            curve_name_cam.append(curve_name_group+'_'+c)
            cmds.curve(n=curve_name_cam[i], p=[pt_3d_coord, pts_cams_coord[i]], d=1)
            curve_shape_cam = cmds.listRelatives(curve_name_cam[i], shapes=True)[0]
            
            # Connection between the first curve point and the selected 3D point to make it real time
            mat2trans = cmds.createNode('decomposeMatrix', n='mat2trans_'+curve_name_cam[i])
            cmds.connectAttr(pt_3d_names[p] + '.worldMatrix[0]', mat2trans + '.inputMatrix', force=1)
            cmds.connectAttr(mat2trans + '.outputTranslate', curve_shape_cam+'.controlPoints[0]', force=1)
            
        cmds.group(curve_name_cam, n=curve_name_group)


def path_3d(*args):
    '''
    Displays 3D path of selected objects.
    For all frames, or for a given number of previous and following frames.
    Last option doesn't work in Maya 2018, due to a bug in this version.
    '''
    allFrames_button_check = cmds.radioButton(allFrames_box, query=True, select=True)
    startT = cmds.playbackOptions(q=1,minTime=1)
    endT = cmds.playbackOptions(q=1,maxTime=1)
    
    pt_3d_names = cmds.ls(sl=True)
    for p in pt_3d_names:
        motion_path, _ = cmds.snapshot(p, motionTrail=1, increment=1, startTime=startT, endTime=endT, n=p+'_')
        
        if allFrames_button_check == True:
            cmds.setAttr(motion_path+".preFrame", 0)
            cmds.setAttr(motion_path+".postFrame", 0)
        else:
            pre = -int(cmds.textField(pre_field, query=1, text=1))
            post = int(cmds.textField(post_field, query=1, text=1))
            cmds.setAttr(motion_path+".preFrame", pre)
            cmds.setAttr(motion_path+".postFrame", post)
        cmds.setAttr(cmds.listRelatives(motion_path)[0]+'.keyframeSize', .1)

  
### WINDOW CREATION
def cam_window():
    '''
    Creates and displays window
    '''
    global number_field, distance_field, width_field, height_field, distance_field, focal_field, disto_field, pxsize_field, binning_field
    global extension_field, scaling_box
    global allFrames_box, pre_field, post_field

    window = cmds.window(title='Camera toolbox')

    ## CAMERA SPECS
    cmds.columnLayout(width=390)
    cmds.text(label='CAMERA SPECS', backgroundColor=[.5,.5,.5], font='boldLabelFont', width=390, height=20)
    # Camera number (only lets us set the slider to 2,4,8,16,32,64])
    number_field = cmds.intSliderGrp('camNb', label='Camera number', field=True, value=8, maxValue=64,
       cc='cmds.intSliderGrp(\'camNb\', edit=True, value= '\
       'min([2,4,8,16,32,64], key=lambda x:abs(x-'\
       'cmds.intSliderGrp(\'camNb\', query=True, value=True) )))')
    # Cameras distance (m)
    distance_field = cmds.textFieldGrp(label='Distance (m)', text='4.5')
    # Image resolution (px)
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 190), (2, 190)])
    width_field = cmds.textFieldGrp(label='Resolution width (px)', text='1280')
    height_field = cmds.textFieldGrp(label='Resolution height (px)', text='768')
    # Focal length (mm)
    cmds.columnLayout(width=390)
    focal_field = cmds.textFieldGrp(label='Focal length (mm)', text='9')
    # Distortion
    disto_field = cmds.textFieldGrp(label='Distortion [-0.2, 2.0]', text='0')
    # Pixel size
    pxsize_field = cmds.textFieldGrp(label='Pixel size (um)', text='5.54')
    # Binning factor
    binning_field = cmds.textFieldGrp(label='Binning factor', text='1')

    ## BUTTONS
    # CAMERA SPECS
    cmds.columnLayout(width=390)
    # Set cameras from specs
    cmds.button(label='Set cameras from specs', ann='Set cameras in scene from values given in specifications fields', width=390, command = setCamsfromSpecs_callback)
    cmds.separator(height=20)

    # OTHER CAMERA ACTIONS
    cmds.text(label='OTHER CAMERA ACTIONS', backgroundColor=[.5,.5,.5], font='boldLabelFont', width=390, height=20)
    # Set cameras from calib
    cmds.button(label='Set cameras from calibration file', ann='Set cameras in scene from chosen .toml calibration file', width=390, command = setCamsfromCal_callback)
    # Save calibration
    cmds.button(label='Save calibration from cameras', ann='Save calibration from cameras in .toml file', width=390, command = saveCalfromCam_callback)
    # Film from cameras
    cmds.button(label='Film from cameras', ann='Film from cameras and save image sequences', width=390, command = filmfromCam_callback)
    # Display videos
    cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1,90), (2, 30), (3,5), (4, 95), (5,160)])
    cmds.text(label='Image extension')
    extension_field = cmds.textField(text='png', width=30)
    cmds.text(label=' ', backgroundColor=[.5,.5,.5])
    scaling_box = cmds.checkBox(label='Apply scaling', backgroundColor=[.5,.5,.5], ann='Image plane size is invariant in translation in the camera view')
    cmds.button(label='Display videos', ann='Display images sequences for illustration purposes', command = setVidfromSeq_callback)

    # OTHER ACTIONS ON OBJECTS
    cmds.columnLayout(width=390)
    cmds.separator(height=20)
    cmds.text(label='GOODIES', backgroundColor=[.5,.5,.5], font='boldLabelFont', width=390, height=20)
    # Reproject selected 3D point
    cmds.button(label='Reproject selected 3D points', ann='Reproject selected 3D points works only if you have cameras in scene, and looks best if you display videos with parameter "Apply scaling" on', width=390, command = reproj_3D)
    # Display path of selected 3D point
    cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1,200), (2, 70), (3,55), (4,25), (5,25)])
    cmds.button(label='Display path of selected 3D points for ', ann='Display path of selected 3D points. Only works for "all frames" in Maya 2018 due to a bug in the version.', command = path_3d)
    cmds.radioCollection()
    allFrames_box = cmds.radioButton(label='all frames', select=True, changeCommand=textOff)
    cmds.radioButton(label='frames')
    pre_field = cmds.textField(text='-50', enable=False)
    post_field = cmds.textField(text='10', enable=False)
    ## Display window
    cmds.showWindow(window)

if __name__ == "__main__":
    cam_window()
