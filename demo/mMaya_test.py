# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 14:22:38 2011

@author: -
"""

#update mMaya object
ob = "chain_0_particle"
part = "chain_0_particleShape" #nParticle
obj = epmv.helper.checkName(obj)
partO=epmv.helper.getMShape(obj)

mol = epmv.mv.Mols[0]
mol.allAtoms.setConformation(step)
v = mol.chains[0].residues.atoms.coords

epmv.helper.updateParticle(partO,vertices=v,faces=None)