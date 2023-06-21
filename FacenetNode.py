import maya.OpenMayaMPx as mpx
import maya.OpenMaya as om

import json
import os

class FacenetTrack(mpx.MPxNode):
    nodeName = 'facenetTrack'
    nodeId = om.MTypeId(0x0000001)

    faceTrack = om.MObject()
    startFrame = om.MObject()
    time = om.MObject()
    landmarks = om.MObject()
    position = om.MObject()
    anim_dict = om.MObject()
    head_dict = om.MObject()
    enableDelta = om.MObject()

    def __init__(self):
        mpx.MPxNode.__init__(self)

    @classmethod
    def creator(cls):
        return mpx.asMPxPtr(FacenetTrack())

    @classmethod
    def initialize(self):
        # init the attribute types
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        cAttr = om.MFnCompoundAttribute()

        # create the faceTrack attribute
        FacenetTrack.faceTrack = tAttr.create('faceTrack', 'ft', om.MFnData.kString)
        FacenetTrack.headTrack = tAttr.create('headTrack', 'ht', om.MFnData.kString)
        
        FacenetTrack.enableDelta = nAttr.create('enableDelta', 'ed', om.MFnNumericData.kBoolean)

        # create the startFrame attr
        FacenetTrack.startFrame = nAttr.create('startFrame', 'sf', om.MFnNumericData.kInt)
        nAttr.setReadable(False)
        nAttr.setWritable(True)
        nAttr.setStorable(True)
        nAttr.setKeyable(True)

        FacenetTrack.time = nAttr.create('time', 't', om.MFnNumericData.kInt)
        nAttr.setReadable(True)
        nAttr.setWritable(True)
        nAttr.setStorable(True)
        nAttr.setKeyable(True)

        # create the outFrame attr
        FacenetTrack.outFrame = nAttr.create('outFrame', 'of', om.MFnNumericData.kInt)
        
        # create the landmarks attr
        FacenetTrack.landmarks = cAttr.create('landmarks', 'lm')
        cAttr.setReadable(True)
        cAttr.setWritable(True)
        cAttr.setStorable(True)
        cAttr.setKeyable(True)
        cAttr.setArray(True)
        position = nAttr.createPoint('position', 'pos')
        cAttr.addChild(position)

        # add all the atributes to the node
        FacenetTrack.addAttribute(FacenetTrack.faceTrack)
        FacenetTrack.addAttribute(FacenetTrack.headTrack)
        FacenetTrack.addAttribute(FacenetTrack.enableDelta)
        FacenetTrack.addAttribute(FacenetTrack.startFrame)
        FacenetTrack.addAttribute(FacenetTrack.time)
        FacenetTrack.addAttribute(FacenetTrack.outFrame)
        FacenetTrack.addAttribute(FacenetTrack.landmarks)

        FacenetTrack.attributeAffects(FacenetTrack.time, FacenetTrack.outFrame)
        FacenetTrack.attributeAffects(FacenetTrack.startFrame, FacenetTrack.outFrame)
        FacenetTrack.attributeAffects(FacenetTrack.time, position)
        FacenetTrack.attributeAffects(FacenetTrack.startFrame, position)
        FacenetTrack.attributeAffects(FacenetTrack.outFrame, position)
        FacenetTrack.attributeAffects(FacenetTrack.enableDelta, FacenetTrack.outFrame)

    def compute(self, plug, data):
        # set the anim data time
        time = data.inputValue(FacenetTrack.time).asInt()
        new_frame = time - data.inputValue(FacenetTrack.startFrame).asInt()

        # need to clamp the new_frame to the anim data frames only
        if new_frame < 0:
            new_frame = 0
        if isinstance(FacenetTrack.anim_dict, dict):
            if new_frame > len(FacenetTrack.anim_dict):
                new_frame = len(FacenetTrack.anim_dict)
        data.outputValue(FacenetTrack.outFrame).setInt(new_frame)

        # need to use the data handle instead of the plug
        if isinstance(FacenetTrack.anim_dict, dict):
            # update all the landmark positions to the current anim data time
            landmark_plug = om.MPlug(self.thisMObject(), FacenetTrack.landmarks)
            try:
                for idx, landmark in enumerate(FacenetTrack.anim_dict[str(new_frame)]):
                    x_pos = landmark[0]
                    y_pos = landmark[1]
                    z_pos = 0.0

                    if data.outputValue(FacenetTrack.enableDelta).asInt():
                        if isinstance(FacenetTrack.head_dict, dict):
                            head_pos = FacenetTrack.head_dict[str(new_frame)]
                            x_pos -= head_pos[0]
                            y_pos -= head_pos[1]

                    landmark_plug.elementByLogicalIndex(idx).child(0).child(0).setFloat(x_pos)
                    landmark_plug.elementByLogicalIndex(idx).child(0).child(1).setFloat(y_pos)
                    landmark_plug.elementByLogicalIndex(idx).child(0).child(2).setFloat(z_pos)
                    data.setClean(landmark_plug)
            except:
                raise

        data.setClean(plug)
    
    def attributeChangedCallback(node, plug, other_plug, client_data):
        if plug == FacenetTrack.faceTrack:
            if os.path.exists(plug.asString()):
                FacenetTrack.anim_dict = dict(json.load(open(plug.asString())))
            else:
                FacenetTrack.anim_dict = None
        
        if plug == FacenetTrack.headTrack:
            if os.path.exists(plug.asString()):
                FacenetTrack.head_dict = dict(json.load(open(plug.asString())))
            else:
                FacenetTrack.head_dict = None

    def postConstructor(self):
        self.callback_id = om.MNodeMessage.addAttributeChangedCallback(self.thisMObject(), FacenetTrack.attributeChangedCallback)

def initializePlugin(obj):
    plugin = mpx.MFnPlugin(obj, 'Justin Phillips', '1.0', 'Any')
    try:
        plugin.registerNode(FacenetTrack.nodeName, FacenetTrack.nodeId, FacenetTrack.creator, FacenetTrack.initialize)
    except:
        raise RuntimeError('Failed to register Facenet plugin')

def uninitializePlugin(obj):
    plugin = mpx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(FacenetTrack.nodeId)
    except:
        raise RuntimeError('Failed to register Facenet plguin')