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