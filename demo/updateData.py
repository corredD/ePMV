
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/updateData.py is part of ePMV.

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
