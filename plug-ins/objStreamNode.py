#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
    ##################################################
    ## Create a node for streaming OBJ files        ##
    ##################################################
    
    Creates a node for streaming OBJ files.
    These obj don't need to have the same amount of vertices along time.
    Uses the plug-in objStreamNode.py
    
    Usage:
    dname = 'C:\Temp'
    bname = 'model_%05d.obj'
    fname = os.path.join(dname,bname)
    outt = cmds.createNode('transform', name='obj_stream')
    outm = cmds.createNode('mesh', name=outt+'Shape', p=outt)
    n = cmds.createNode('objStreamNode')
    cmds.setAttr(n+'.fname',fname,type='string')
    cmds.connectAttr('time1.outTime', n+'.index')
    cmds.connectAttr(n+'.outMesh', outm+'.inMesh')
'''


## INIT
import maya.cmds as cmds
import sys
import os
import maya.api.OpenMaya as om
import numpy as np

## AUTHORSHIP INFORMATION
__author__ = "Lionel Reveret"
__copyright__ = "Copyright 2021, Maya-Mocap"
__credits__ = ["Lionel Reveret"]
__license__ = "BSD 3-Clause License"
__version__ = "0.1"
__maintainer__ = ["Lionel Reveret", "David Pagnon"]
__email__ = ["lionel.reveret@inria.fr", "contact@david-pagnon.com"]
__status__ = "Development"


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

#
# MAIN CLASS DECLARATION FOR THE CUSTOM NODE:
#
class objStreamNode(om.MPxNode):
    id = om.MTypeId(0x03031)
    aOutMesh = None
    aIndex = None
    aFname = None
    
    def __init__(self):
        om.MPxNode.__init__(self)

    # FOR CREATING AN INSTANCE OF THIS NODE:
    @staticmethod
    def cmdCreator():
        return objStreamNode()

    # INITIALIZES THE NODE BY CREATING ITS ATTRIBUTES:
    @staticmethod
    def initialize():
        # CREATE AND ADD ".outMesh" ATTRIBUTE:
        outMeshAttrFn = om.MFnTypedAttribute()
        objStreamNode.aOutMesh = outMeshAttrFn.create("outMesh", "m", om.MFnData.kMesh)
        outMeshAttrFn.storable = False
        outMeshAttrFn.keyable = False
        outMeshAttrFn.readable = True
        outMeshAttrFn.writable = False
        om.MPxNode.addAttribute(objStreamNode.aOutMesh)

        # CREATE AND ADD ".index" ATTRIBUTE:
        indexAttrFn = om.MFnNumericAttribute()
        objStreamNode.aIndex = indexAttrFn.create("index", "i", om.MFnNumericData.kInt, 0)
        indexAttrFn.storable = True
        indexAttrFn.keyable = True
        indexAttrFn.readable = True
        indexAttrFn.writable = True
        om.MPxNode.addAttribute(objStreamNode.aIndex)

        # CREATE AND ADD ".fname" ATTRIBUTE:
        stringFn = om.MFnStringData()
        defaultText = stringFn.create("model_%05d.obj")#"seq040.%05d.obj"
        fnameAttrFn = om.MFnTypedAttribute()
        objStreamNode.aFname = fnameAttrFn.create("fname", "f", om.MFnData.kString, defaultText)
        om.MPxNode.addAttribute(objStreamNode.aFname)

        # DEPENDENCY RELATIONS FOR ".index":
        om.MPxNode.attributeAffects(objStreamNode.aIndex, objStreamNode.aOutMesh)
        om.MPxNode.attributeAffects(objStreamNode.aFname, objStreamNode.aOutMesh)

    # COMPUTE METHOD'S DEFINITION:
    def compute(self, plug, data):
        assert(isinstance(data.context(), om.MDGContext))
        assert(data.setContext(data.context()) == data)

        # DO THE COMPUTE ONLY FOR THE *OUTPUT* PLUGS THAT ARE DIRTIED:
        if plug == objStreamNode.aOutMesh :
            # READ IN ".fname" DATA:
            fnameDataHandle = data.inputValue(objStreamNode.aFname)
            fname_format = fnameDataHandle.asString()

            # READ IN ".index" DATA:
            indexDataHandle = data.inputValue(objStreamNode.aIndex)
            index = indexDataHandle.asInt()

            fname = fname_format % index
            nl = 0
            pts = []
            uvs = []
            ptsIds = []
            uvsIds = []
            pcount = []
            if os.path.isfile(fname) :
                lines = [ line for line in open(fname) ]
                nl = len(lines)
                for line in lines :
                    if line[:2]=='v ' :
                        pts += [ list(map(float, line[2:].split())) ]
                    if line[:3]=='vt ' :
                        uvs += [ list(map(float, line[3:].split())) ]
                    elif line[:2]=='f ' :
                        ids = [ list(map(int,tok.split('/'))) for tok in line[2:].split() ]
                        [va,ta],[vb,tb],[vc,tc] = ids
                        ptsIds += va,vb,vc
                        uvsIds += ta,tb,tc
                        pcount += [ 3 ]
            nv = len(pts)
            nt = len(uvs)
            npId = len(ptsIds)
            print('fname=[%s] nl=%d nv=%d nt=%d npId=%d' % (fname, nl, nv, nt, npId))

            dataCreator = om.MFnMeshData()
            newOutputData = dataCreator.create()

            if nv>0 :
                ptsIds = np.array(ptsIds)-1
                uvsIds = np.array(uvsIds)-1
                uvs = np.array(uvs).T

                pts = om.MFloatPointArray(pts)
                uvs = [ om.MFloatArray(uvs[0]), om.MFloatArray(uvs[1]) ]
                ptsIds = om.MIntArray(ptsIds)
                uvsIds = om.MIntArray(uvsIds)
                pcount = om.MIntArray(pcount)

                if nv<100 :
                    print('pts='),pts
                    print('uvs='),uvs
                    print('ptsIds='),ptsIds
                    print('uvsIds='),uvsIds
                    print('pcount='),pcount

                meshFn = om.MFnMesh()
                if nt>0 :
                    newMesh = meshFn.create(pts, pcount, ptsIds, uValues=uvs[0], vValues=uvs[1], parent=newOutputData)
                    meshFn.assignUVs(pcount, uvsIds)
                else :
                    newMesh = meshFn.create(pts, pcount, ptsIds, parent=newOutputData)

            # WRITE OUT ".position" DATA:
            outputHandle = data.outputValue(objStreamNode.aOutMesh)
            outputHandle.setMObject(newOutputData)
            data.setClean(plug)

        else:
            return None # let Maya handle this attribute


# INITIALIZES THE PLUGIN BY REGISTERING THE COMMAND AND NODE:
#
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode("objStreamNode", objStreamNode.id, objStreamNode.cmdCreator, objStreamNode.initialize)
    except:
        sys.stderr.write("Failed to register node\n")
        raise

#
# UNINITIALIZES THE PLUGIN BY DEREGISTERING THE COMMAND AND NODE:
#
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(objStreamNode.id)
    except:
        sys.stderr.write("Failed to deregister node\n")
        raise

