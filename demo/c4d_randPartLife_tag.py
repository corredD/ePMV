
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/c4d_randPartLife_tag.py is part of ePMV.

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
Created on Thu Aug 18 13:04:29 2011

@author: ludovic autin

C4D python tag test for updating the current PS using  random value for life
As Pyro use life for the grdient coloring...

"""

import c4d
#Welcome to the world of Python
import random
#BaseTime is in second

#linear gradient 0 - N/2 - N
#
def main():
    random.seed(24)
    PS = doc.GetParticleSystem()
    cframe = doc.GetTime().GetFrame(doc.GetFps()) #10->300,1->30
    N = PS.NumParticles()
    if cframe == 0 :
        ids = range(N)
        life = [c4d.BaseTime(10.0)]*N
        map(PS.SetLife,ids,life)
    else :
        #set default ages for everyone
        ids = range(N)
        dval = 0.
        ages = [c4d.BaseTime(dval)]*N
        map(PS.SetAge,ids,ages)
        #randomly change life on a pacth, always same patch?
        ids = range(int(N/3),int(N/2))
        nN = int(len(ids))
        val = cframe/30.0#random.random()*10.0
        ages = [c4d.BaseTime(val)]*nN
        map(PS.SetAge,ids,ages)
        
        ids = range(int(N/2),int(N))
        nN = int(len(ids))
        val = cframe/60.0#random.random()*10.0
        ages = [c4d.BaseTime(val)]*nN
        map(PS.SetAge,ids,ages)