
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/extension/_prody/_prody.py is part of ePMV.

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
Created on Thu Nov 17 14:02:42 2011

@author: -
"""
import numpy
import prody
from prody import * 
#cant do the computatio interactivly
#can probably do the computation online and just display the result

class _prodymodel(object):
    keywords = {
        "id" :0 ,
        "mode" :0,
        "rmsd" : 0.8,
        "nbconf" : 10,
        "conf" : "allatom",
        "cutoff" : 15.0,
        "gamma" : 1.0,#spring constant
        "gammaStructure" : False,
        "sample" : "sample",#or traverse
        "center" : False,
    }
    
    def __init__(self,pdbfile,*args,**kw):
        self.anm = None  
        self.pmvmodel = None
        self.oricoords = None
        self.first = True
#        self.center = False
        for k in self.keywords :
            setattr(self,k,self.keywords[k])
        self.Set(**kw)
        if pdbfile is not None :
            self.load(pdbfile)
            self.setNM()
            
    def load(self,filename):
        self.filname = filename
        self.model = prody.parsePDB(self.filname, model=1) 
        print ("self.center",self.center)
        if self.center :
#            c = calcCenter(self.model) 
            moveAtoms(self.model, to=numpy.zeros(3))
        self.ca_model = self.model.select('protein and name CA')#what about DNA
        
    def setNM(self,):
        self.anm = prody.ANM(self.filname+str(self.id))
    
    def setPMVmodel(self,model):
        self.pmvmodel = model
    
    def Set(self,**kw):
        for k in kw :
            if k in self.keywords:
                setattr(self,k,kw[k])
        if "pmvmodel" in kw :
            self.setPMVmodel(kw["pmvmodel"])
             
    def computeNormalMode(self,) :         
        if self.anm is None :
            return
        if self.gammaStructure:
            self.gamma = prody.GammaStructureBased(self.ca_model)
        self.anm.buildHessian(self.ca_model, gamma=self.gamma, cutoff=self.cutoff)
        self.anm.calcModes()
        #extrapole
        self.bb_anm, self.bb_atoms = prody.extrapolateModel(self.anm, self.ca_model, self.model.select(self.conf))#self.conf))
        self.nbMode = self.anm.getNumOfModes()
             
    def applyMode(self,idMode):
        if idMode > self.nbMode:
            return
        #sample?should gave 10
        #or should I use traverseMode
        #should I redo the extrapolation ?
        self.bb_anm, self.bb_atoms = prody.extrapolateModel(self.anm, self.ca_model, self.model.select(self.conf))#self.conf))
        self.nbMode = self.anm.getNumOfModes()        
        if self.sample == "sample" :
            ensemble = prody.sampleModes(self.bb_anm[idMode], self.bb_atoms, n_confs=self.nbconf, rmsd=self.rmsd)
        elif  self.sample == "traverse" :
            ensemble = prody.traverseMode(self.bb_anm[idMode], self.bb_atoms, n_steps=int(self.nbconf/2), rmsd=self.rmsd)    
        coords=ensemble.getCoordsets() 
        nC = len(coords)   #should beequal to nbconf 
        self.pmvmodel.allAtoms.setConformation(0)
        if self.first:
            self.oricoords  = numpy.array(self.pmvmodel.allAtoms._coords[:])
            self.first = False
        else :
            self.pmvmodel.allAtoms._coords = self.oricoords.tolist()
            #self.pmvmodel.allAtoms._coords = numpy.concatenate(([oricoords,],coords),axis=0)        
        #if a gui is available shoud update it
        #use current sel
        for i,c in enumerate(coords):
            if self.conf == "ca" :
                if len(c) != len(self.pmvmodel.allAtoms.get("CA").coords):
                    return
                self.pmvmodel.allAtoms.get("CA").addConformation(c[:])
            elif self.conf == "protein and ca" :  
                self.pmvmodel.chains.residues.get("aminoacids").atoms.get("CA").addConformation(c[:])
            elif self.conf == "protein" :
                self.pmvmodel.chains.residues.get("aminoacids").atoms.addConformation(c[:])
                #self.pmvmodel.allAtoms.get("aminoacids").addConformation(c[:])
            else :#all
                if len(c) != len(self.pmvmodel.allAtoms.coords):
                    return
                self.pmvmodel.allAtoms.addConformation(c[:])
        