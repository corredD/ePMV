
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/md_rot_update.py is part of ePMV.

    ePMV is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ePMV.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
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
