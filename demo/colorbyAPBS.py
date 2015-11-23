
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/colorbyAPBS.py is part of ePMV.

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
Created on Fri Oct  1 08:13:38 2010

@author: Ludovic Autin

color a MSMS surface or any geometry according an APBS electrostatic grid (.dx)

"""
#1-get the grid or use the current grid ?
grid = epmv.gui.current_traj[0]# self.grids3D.values()[0]
#2-get the surface from the current mol ?
mol = epmv.gui.current_mol
if 'MSMS-MOL'+mol.name in mol.geomContainer.geoms:
    surf = mol.geomContainer.geoms['MSMS-MOL'+mol.name]# self.Mols[0].geomContainer.geoms['MSMS-MOL1TIMtr']
else :
    epmv.gui.displaySurf()
    surf = mol.geomContainer.geoms['MSMS-MOL'+mol.name]
#3-color,offset apply on vertex normal for the volume projection, stddev scale factor apply on the 
#standar deviation value
epmv.APBS2MSMS(grid,surf=surf,offset=1.0,stddevM=5.0)
