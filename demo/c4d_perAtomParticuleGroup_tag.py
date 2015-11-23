
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/c4d_perAtomParticuleGroup_tag.py is part of ePMV.

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
Created on Mon Aug 15 15:16:22 2011

@author: Ludovic autin
if first frame create PS group per atoms for the molecule atoms
and overwrite the particle posiion to be at atoms position
This tag could be used to create Spher or geometry instance for every particle

"""
import c4d
#Welcome to the world of Python


def main():
    PS = doc.GetParticleSystem()
    
    epmv = c4d.mv.values()[0]
    ob = op.GetObject()
    mx = ob.GetMg()
    mol = epmv.mv.getMolFromName(ob.GetName())
    cframe = doc.GetTime().GetFrame(doc.GetFps())
#PS = epmv.helper.getCurrentScene().GetParticleSystem()
    if cframe == 0 :
        from Pmv.pmvPalettes import AtomElements
        ats = mol.allAtoms
        PS = epmv.helper.particle(at,ats.coords,radius=ats.radius,hostmatrice=mx)
        molgrp = epmv.helper.createGroup("PS"+mol.name,[1.,1.,1.])
        listea = ["C","O","N","S"]
        for a in listea:
            g = epmv.helper.createGroup("PS"+mol.name+a,color=AtomElements[a[0]],parent = molgrp,PS=PS)
            tpg = epmv.helper.newTPgeometry("gPS"+mol.name+a,group = g)
            listeID = [i for i,at in enumerate(mol.allAtoms) if at.element == a]
#            ats = mol.allAtoms.get(at+"*")
            #map(PS.SetGroup,listeID,[g,]*len(listeID))
            epmv.helper.setParticlProperty("group",listeID,[g,]*len(listeID),PS=PS)
        mol.has_particls = True
#        mol.particleg=pg
        return
    if hasattr(mol,"has_particls") and mol.has_particls:
        #hostC = map(epmv.helper.FromVec,mol.allAtoms.coords)
        hostC = [epmv.helper.FromVec(c)*mx for c in mol.allAtoms.coords]
        ids = range(len(mol.allAtoms))
#        epmv.helper.setProperty("position",ids,hostC)
        map(PS.SetPosition,ids,hostC)