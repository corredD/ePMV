# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 15:16:22 2011

@author: -
"""
import c4d
#Welcome to the world of Python

import numpy
from math import pi

def main():
    #rotate ?
    #initially 60 frame 0 -> 360
    #6degree per frame
    #nb dynamic frame - > 10-30-60 dyn
    #md step jump 4
    #nb rotation frame -> 60?
    #every 30 frame one new rotation
    #total nb of frame = nbD*nbR
    fullrot = 2*pi
    nbRot = 60
    nbDyn = 30
    Nframes = nbRot*nbDyn
    mdstep = 4
    epmv = c4d.mv.values()[0]
    epmv.helper.doc = doc
    ob = op.GetObject()
    mol = epmv.mv.getMolFromName(ob.GetName())   
    traj = epmv.gui.current_traj
    cframe = doc.GetTime().GetFrame(doc.GetFps()) 
    #defeine rotation in radians
    #get rotation from cframe
    modulo = cframe % nbDyn
    print "cframe",cframe,modulo
    if modulo == 0 :
        r = (float(cframe)/float(Nframes))*fullrot
        print r
        epmv.helper.rotateObj(ob,[r,0.,0.]) #x,y,z rotation
    #get the md step we want
    if modulo <= nbDyn/2:
        epmv.updateData(traj,mdstep*int(modulo))#traj[0].player.applyState(int(cframe))
    else :
        epmv.updateData(traj,mdstep*int(nbDyn-modulo))#traj[0].player.applyState(int(end-cframe))
