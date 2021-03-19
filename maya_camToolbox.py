'''
Camera toolbox.
Let you 
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
import toml
import cv2


## FUCTIONS
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

    
def applyImg(plane, filename, sequence=False):
    '''
    Apply image (or image sequence) texture to plane.
    Inspired from https://stackoverflow.com/questions/15268511/maya-python-place-image-on-a-plane.
    '''
    shader = cmds.shadingNode('surfaceShader', asShader=True)
    SG = cmds.sets(empty=True, renderable=True, noSurfaceShader=True, name=shader+"SG")
    cmds.connectAttr(shader+'.outColor', SG+".surfaceShader", force=True)
    img = cmds.shadingNode('file', asTexture=True)
    cmds.setAttr(img+'.fileTextureName', filename, type='string')
    cmds.connectAttr(img+'.outColor', shader+'.outColor', force=True)
    
    cmds.sets(plane, edit=True, forceElement=SG)
    if sequence:
        ufe = cmds.setAttr(img+'.useFrameExtension', True)
        cmds.expression( s='{}.frameExtension=frame'.format(img) )

        
def setCamsfromSpecs_callback(*args):
    '''
    Set cameras from specs.
    Prompts a set of custom specs, and creates cameras.
    Another possibility would be to set cameras at the center of polyPlatonicSolid (not implemeted).
    '''
    # RETRIEVE SPECS
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
    
    # SET CAMERAS
    cams = []
    for c in range(number):
        cam, camShape = cmds.camera(n='cam_%d'%(c+1), focalLength=fm, horizontalFilmAperture = W*px_size*39.3701, verticalFilmAperture = H*px_size*39.3701) # m->inch : *39.3701
        cams.append(cam)
        cmds.setAttr(camShape + '.aiRadialDistortion', disto) #1 for GoPro (roughly)
        if number == 2 or number == 4:
            ang = 90*c * np.pi/180
            cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1.5])
        elif number == 8:
            ang = 45*c * np.pi/180
            cmds.xform(cam, translation = [distance*np.cos(ang),distance*np.sin(ang), 1.5])
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
    
    # OPEN FILE DIALOG (fm = 0 pour sauver plutot qu'ouvrir)
    singleFilter = "Toml calibration files (*.toml)"
    path = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, cap="Open Calibration File", fm=1)[0]
    # RETRIEVE CALIBRATION
    S, D, K, R, T, P = retrieveCal(path)
    
    # SET CAMERAS
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

        cmds.setAttr(camShape + '.aiRadialDistortion', -D['cam_%d' %(c+1)][0]*4) # Cuisine pour passer de la distorsion de maya (fisheye?) a celle de opencv (pinhole?)
        cmds.xform(cam, m=Mlist)
        cmds.setAttr("defaultResolution.width", W) 
        cmds.setAttr("defaultResolution.height", H) 
        cmds.select(cam)
        cmds.rotate(180,0,0, objectSpace=1, relative=1)

    cmds.select(cams)
    cmds.group(n='cameras')

    
def saveCalfromCam_callback(*arg):
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

        
def filmfromCam_callback(*arg):
    '''
    Film playblast image sequences from each cameras in scene.
    '''
    cmds.select('cameras')
    list_cams = cmds.ls(sl=1, dag=1, type='transform')[:-1]
    size = cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")

    path = cmds.fileDialog2(dialogStyle=2, cap="Choose video saving folder", fm=3)[0]
    # eg: G:\Op2Ani\191209_6miqus_xsens\dance_2\seq003
    
    videos_dir = os.path.join(path, '%d_cams_maya'%len(list_cams))
    if not os.path.exists(videos_dir): 
        os.mkdir(videos_dir) 
    else:
        confirm = cmds.confirmDialog( title='Confirm', message='Do you want to overwrite the folder?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if confirm == 'No':
            return
            
    cmds.grid(toggle=0)
    cmds.setAttr('cameras.visibility', 0)

    for c in range(len(list_cams)):
        cam_dir = os.path.join(videos_dir, os.path.basename(path)+'_cam%d_img'%(c+1))
        if not os.path.exists(videos_dir): os.mkdir(videos_dir) 

        cmds.select('cam_%d'%(c+1))
        cmds.lookThru('cam_%d'%(c+1))
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32) # *.png
        
        cmds.playblast(format='image', wh=size, percent=100, f=os.path.join(cam_dir,os.path.basename(path)+'_cam%d'%(c+1)), viewer=False)
    
    cmds.grid(toggle=1)
    cmds.setAttr('cameras.visibility', 1)

    
def setVidfromSeq_callback(*arg):
    '''
    Display image sequences behind each camera in scene.
    '''
    px_size = float(cmds.textFieldGrp(pxsize_field, query=1, text=1)) * 1e-6
    binning_factor = float(cmds.textFieldGrp(binning_field, query=1, text=1))
    
    path = cmds.fileDialog2(dialogStyle=2, cap="Choose root directory of videos folders", fm=3)[0]
    img_dirs = list(filter( lambda item: 'img' in item, next(os.walk(path))[1] ))
    img_dirs_full = [os.path.join( path, dir ) for dir in img_dirs]
    img_files_per_cam = [glob.glob(os.path.join(dir,"*.png")) for dir in img_dirs_full]

    ## Change image names to comply with 'name.XXX.png'
    while True:
        try: 
            os.path.basename(img_files_per_cam[0][0]).split('.')[-2] # verif .XXX.
            break
        except:
            filename_base = '_'.join([os.path.basename(path), 'cam_%d' %(c+1)])
            filename_ext = os.path.splitext(img_files_per_cam[0][0])[1]
            for c in range(len(img_dirs_full)): # Pour chaque cam
                for i, f in enumerate(img_files_per_cam[c]):
                    os.rename(f, os.path.join(img_dirs_full[c], ''.join([filename_base, '.%05d'%i, filename_ext])) )
            img_files_per_cam = [glob.glob(os.path.join(dir,"*.png")) for dir in img_dirs_full]

    ## Set videos in scene
    vidPlane=[]
    for c in range(len(img_dirs_full)): # Pour chaque cam
        # plane size
        W = cmds.camera('cam_%d' %(c+1), query=True, horizontalFilmAperture=True) / (px_size*39.3701) / binning_factor
        H = cmds.camera('cam_%d' %(c+1), query=True, verticalFilmAperture=True) / (px_size*39.3701) / binning_factor
        vidPlane.append( cmds.polyPlane(n='vid_%d' %(c+1), ax=[0,0,1], w=W*px_size, h=H*px_size)[0] )
        # set plane at camera locations
        camMat = cmds.xform('cam_%d' %(c+1), query=True, matrix=True)
        cmds.xform(vidPlane[c], m=camMat)
        # scale plane according to distance
        distance = cmds.xform('cam_%d' %(c+1), q=1, os=1, translation=1)[2]
        fm = cmds.camera('cam_%d' %(c+1), q=1, focalLength=True)        
        cmds.setAttr(vidPlane[c]+'.scaleX',  distance/(fm*1e-3) )   # D/fm
        cmds.setAttr(vidPlane[c]+'.scaleY', distance/(fm*1e-3) )
        cmds.makeIdentity(vidPlane[c], apply=True, scale=True)
        # rotate plane
        cmds.select(vidPlane[c])
        # apply img texture to plane
        applyImg(vidPlane[c], img_files_per_cam[c][0], sequence=True)

    cmds.select(vidPlane)
    cmds.group(n='videos') 

    
### WINDOW CREATION
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
distance_field = cmds.textFieldGrp(label='Distance (m)', text='4.5' )
# Image resolution (px)
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 190), (2, 190)])
width_field = cmds.textFieldGrp(label='Resolution width (px)', text='1280')
height_field = cmds.textFieldGrp(label='Resolution height (px)', text='768')
# Focal length (mm)
cmds.columnLayout(width=390)
focal_field = cmds.textFieldGrp(label='Focal length (mm)', text='9' )
# Distortion
disto_field = cmds.textFieldGrp(label='Distortion [-0.2, 2.0]', text='0' )
# Pixel size
pxsize_field = cmds.textFieldGrp(label='Pixel size (um)', text='5.54' )
# Binning factor
binning_field = cmds.textFieldGrp(label='Binning factor', text='1' )

## BUTTONS
cmds.columnLayout(width=390)
# Set cameras from specs
cmds.button(label='Set cameras from specs', ann='Set cameras in scene from values given in specifications fields', width=390, command = setCamsfromSpecs_callback)

cmds.separator(height=20)
cmds.text(label='OTHER ACTIONS', backgroundColor=[.5,.5,.5], font='boldLabelFont', width=390, height=20)
# Set cameras from calib
cmds.button(label='Set cameras from calibration file', ann='Set cameras in scene from chosen .toml calibration file', width=390, command = setCamsfromCal_callback)
# Save calibration
cmds.button(label='Save calibration from cameras', ann='Save calibration from cameras in .toml file', width=390, command = saveCalfromCam_callback)
# Film from cameras
cmds.button(label='Film from cameras', ann='Film from cameras and save image sequences', width=390, command = filmfromCam_callback)
# Display videos
cmds.button(label='Display videos', ann='Display images sequences for illustration purposes', width=390, command = setVidfromSeq_callback)

## Display window
cmds.showWindow(window)








