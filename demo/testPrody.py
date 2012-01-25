# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 14:14:58 2011

@author: -
"""
#http://www.csb.pitt.edu/ProDy/contents.html
import prody
p38ca = prody.parsePDB('1p38', subset='ca')
anm = prody.ANM('1p38')
anm.buildHessian(p38ca)
anm.calcModes()

#traverseMode() function generates conformations along a single normal mode. 
#Conformations are generated in both directions along the given mode. 
#rmsd argument is used to set the RMSD distance to the farthest conformation.
#Let’s generate 10 conformations along ANM mode 1:
trajectory = prody.traverseMode(anm[0], p38ca, n_steps=5, rmsd=2.0)
coords=trajectory.getCoordsets()
#conformation...

#dumb->read in epmv or read on the fly?
p38traj = p38ca.copy()
p38traj.delCoordset(0)
p38traj.addCoordset( trajectory )
prody.writePDB('p38_mode1_trajectory.pdb', p38traj)
def computeNormalMode(userfilenamein="",userfilenameout="NMA.pdb", usermode=0,userrmsd=0.8, usernbconf=5, conf="allatom", usercutoff=15.0, usergamma=1.0) : 
	mystruct = prody.parsePDB(userfilenamein, model=1)
	mystruct_ca = mystruct.select('protein and name CA')

	anm = prody.ANM(userfilenamein+str(usermode))
	anm.buildHessian(mystruct_ca, gamma=usergamma, cutoff=usercutoff)
	anm.calcModes()
	
	bb_anm, bb_atoms = extrapolateModel(anm, mystruct_ca, mystruct.select(conf))
	ensemble = sampleModes(bb_anm[usermode], bb_atoms, n_confs=usernbconf, rmsd=userrmsd)
	nmastruct = mystruct.copy( bb_atoms )
	nmastruct.addCoordset(ensemble)
			
	writePDB(userfilenameout, nmastruct)