
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/molAdaptor.py is part of ePMV.

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
Created on Mon Dec 12 14:06:41 2011

@author: -
"""
class aGeom:
    def __init__(self,name=None,vertices=None,faces=None,
                 normals=None,colors=None,pov = None):
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.colors = colors
        self.normals = normals
        self.pov = pov
        
    def Set(name=None,vertices=None,faces=None,normals=None,colors=None,pov =None):
        if name is not None :
            self.name = name
        if vertices is not None :
            self.vertices = vertices
        if faces is not None :
            self.faces = faces
        if colors is not None :
            self.colors = colors
        if normals is not None :
            self.normals = normals        
        if pov is not None :
            self.pov = pov
            
class molAdaptor:
    """
    The general pymol adaptor.
    
    from ePMV.PyMol.pymolAdaptor import pymolAdaptor
    pym = pymolAdaptor(debug=1)
    mol = pym.readMolecule("/Users/ludo/blenderKTF/1CRN.pdb")
    geom = pym.displayExtrudedSS(mol)#cartoon pym.cmd.show_as("cartoon",mol)
    #create a polygon and color it
    selection :/object-name/segi-identifier/chain-identifier/resi-identifier/name-identifier

    ...
    """
    def __init__(self,debug=0):
        #look for PYMOL_PATH
        self.start_engine()
        self.Mols = {}
        self.cmd = None
        self.molengine = self.start_engine()      
        self.debug = debug
        self.viewmat = None#numpy.array(self.cmd.get_view(quiet=1))

    def start_engine(self,):
        pass
    
    def Load(self,filename,name):
        pass
    
    def readMolecule(self,filename,name=None):
        if name is None :
            name = filename.split('/')[-1].split('.')[0]
        self.Load(filename,name)
        self.Mols[name]={}
        return name


    def displayExtrudedSS(self,name,fancyH=True,color=""):
        #color "ss"
        #self.cmd.hide("all")
        geom = None
        return geom

    def get_povray(self):
        return None

    def get_view(self):
        return None
                
    def parsePOVmesh2(self,name,rep="cartoon"):
        return None


