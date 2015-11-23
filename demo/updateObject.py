
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/updateObject.py is part of ePMV.

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
Created on Tue May  3 12:07:08 2011

@author: Ludovic Autin
Script to update a current epmv mesh object using an equivalent 3d mesh loaded.
"""
#for each chain
listeObjectLoaded=["BDNA_2:A_line","BDNA_2:B_line"]
listeObjectToUpdate=["BDNA:A_line","BDNA:B_line"]
for i in range(2):
    nameOfObjectLoaded=listeObjectLoaded[i]
    nameOfObjectToUpdate=listeObjectToUpdate[i]

    object_to_update = epmv.helper.getObject(nameOfObjectToUpdate)
    object_loaded = epmv.helper.getObject(nameOfObjectLoaded)

    v = epmv.helper.getMeshVertices(object_loaded,transform=True)

    #this update the vertices according object verticse and transformation matrix
    epmv.helper.updatePoly(object_to_update,vertices=v)

# we can  apply it to the molecule.:
mol = epmv.mv.getMolFromName("BDNA")
epmv.updateMolAtomCoord(mol,types = 'lines')