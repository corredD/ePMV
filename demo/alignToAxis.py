# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 09:29:27 2016

@author: ludovic autin
align PDB file to the symetrical axis obtainewd from http://symd.nci.nih.gov/
"""

import sys
import os
import numpy as np
#import c4d

sys.path.append("/home/ludo/Tools/mgltools_x86_64Linux2_latest/MGLToolsPckgs/")
sys.path.append("/home/ludo/Tools/mgltools_x86_64Linux2_latest/MGLToolsPckgs/PIL/")
#windows path
sys.path.append("C:\Users\ludov\AppData\Roaming\MAXON\CINEMA 4D R17_8DE13DAD\plugins\ePMV\mgl64\MGLToolsPckgs")
sys.path.append("C:\Users\ludov\AppData\Roaming\MAXON\CINEMA 4D R17_8DE13DAD\plugins\ePMV\mgl64\MGLToolsPckgs\PIL")

from mglutil.math.rotax import rotVectToVect
#mol0,1,2 are the ouput of the server, separated with pymol
#mol3 is the input query
axis_chain = self.Mols[2]
axis_coords = np.array(self.Mols[2].allAtoms.coords)
axis_vector = epmv.helper.normalize(axis_coords[2]-axis_coords[0])
#align axis_vector to up vector 0,1,0
up = np.array([0,1,0])
M = rotVectToVect(axis_vector,up)
L,M1= epmv.helper.getTubePropertiesMatrix(axis_coords[0],axis_coords[2])
mx = epmv.helper.FromMat(M1.transpose())
#inverse
m2=np.linalg.inv(M1).transpose()
#apply this matrix to atom, save new pdb.
new_coords = epmv.helper.ApplyMatrix( self.Mols[0].allAtoms.coords, m2 )
self.Mols[0].allAtoms.updateCoords(new_coords)
new_coords = epmv.helper.ApplyMatrix( self.Mols[1].allAtoms.coords, m2 )
self.Mols[1].allAtoms.updateCoords(new_coords)
new_coords = epmv.helper.ApplyMatrix( self.Mols[3].allAtoms.coords, m2 )
self.Mols[3].allAtoms.updateCoords(new_coords)

        