# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 15:16:22 2011

@author: -
"""
import c4d
#Welcome to the world of Python

import numpy

def main():
    #rotate ?
    epmv = c4d.mv.values()[0]
    epmv.helper.doc = doc
    ob = op.GetObject()
    mol = epmv.mv.getMolFromName(ob.GetName())   
    traj = epmv.gui.current_traj
    cframe = doc.GetTime().GetFrame(doc.GetFps())
    start = 0
    end = 60
    if cframe <= end/2:
        epmv.updateData(traj,2*int(cframe))#traj[0].player.applyState(int(cframe))
    else :
        epmv.updateData(traj,2*int(end-cframe))#traj[0].player.applyState(int(end-cframe))
