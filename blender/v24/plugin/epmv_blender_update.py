
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/blender/v24/plugin/epmv_blender_update.py is part of ePMV.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 09:36:40 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import Blender

#first get epmv
rdict = Blender.Registry.GetKey('mv', False)
epmv = rdict['epmv']

sc=epmv.helper.getCurrentScene()
if epmv.synchro_timeline : 
    traj = epmv.gui.current_traj
    frame = Blender.Get('curframe')
    seconds = int(Blender.Get('curframe')/25.0)+1
    st,ft=epmv.synchro_ratio
    if (frame % ft) == 0:   
        step = frame * st
        epmv.updateData(traj,step)
else :
    #get selected object
    slist = epmv.helper.getCurrentSelection()
    if not slist : 
       #do nothing
       pass
    else :
        for l in slist:
            print(l)
        epmv.updateCoordFromObj(slist,debug=True)
#epmv.helper.update()
