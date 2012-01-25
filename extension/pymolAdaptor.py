# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:46:30 2011

@author: -
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 10:07:51 2011

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import numpy
from ePMV.molAdaptor import molAdaptor,aGeom

#pymol is in /Library/python2.5/site=pacakges   
#import sys
#sys.path.append("/Library/Python/2.5/site-packages/")

class pymolAdaptor(molAdaptor):
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
    def start_engine(self,):
        import os
        import sys
        if sys.platform == "win32" :
            os.environ['PYMOL_PATH'] = "C:\Python26\lib\site-packages\pymol"
        import pymol
        print("ok launch pymol")
        pymol.pymol_argv[1] = '-qcGi'
        import __main__
#        __main__.pymol = pymol
        print(dir(__main__))
        print(__name__)
        pymol.finish_launching()
        import sys
        print("done")
        self.cmd = pymol.cmd
        self.fragments = {'formamide':(3,1),
                        'acetylene':(2,0),
                        'formamide':(3,1),
                        'cyclobutane':(4,0),
                        'cyclopentane':(5,0),
                        'cyclopentadiene':(5,0),
                        'cyclohexane':(7,0),
                        'cycloheptane':(8,0),
                        'methane':(1,0),
                        'benzene':(6,0),
                        'sulfone':(6,0)
                        }        
        return pymol
        
    def Load(self,filename,name):
        self.cmd.load(filename,name)
    
    def readMolecule(self,filename,name=None):
        if name is None :
            name = filename.split('/')[-1].split('.')[0]
        self.Load(filename,name)
        self.Mols[name]={}
        return name

    def toggleFancy(self,fancyH):
        val = int(fancyH)
        self.cmd.do("set cartoon_fancy_helices, "+str(val))

    def get_view(self):
        return numpy.array(self.cmd.get_view(quiet=1))
        
    def get_povray(self):
        pov = self.cmd.get_povray()[1]
        lines = pov.split("\n")
        return lines

    def displayExtrudedSS(self,name,fancyH=True,color=""):
        #color "ss"
        #self.cmd.hide("all")
        self.toggleFancy(fancyH)
        print(name)
        self.cmd.show_as("cartoon",name)
        if color == "ss":
            self.cmd.color("red","ss h")
            self.cmd.color("yellow","ss s")
            self.cmd.color("red","ss l+''")
            self.cmd.do("set cartoon_discrete_colors, 1")
            self.cmd.do("set cartoon_highlight_color, red")
        elif color == "publication":
            self.pymol.preset.publication(name,_self=self.cmd)
            self.cmd.dss(name)
#        self.cmd.refresh()
        self.cmd.do("set light_count, 0")
        self.cmd.do("set ambient, 0")
        geom = self.parsePOVmesh2(name)
        self.Mols[name]["ss"] = geom
#        self.cmd.do("set light_count, 2")
        return geom
    
    def parsePOVmesh2(self,name,rep="cartoon"):
        #undisplay everything
        self.viewmat = numpy.array(self.cmd.get_view(quiet=1))        
        #display only name in representation rep
        pov = self.cmd.get_povray()[1]
        lines = pov.split("\n")
        done = False
        vertices=[]
        faces=[]
        normals=[]
        colors=[]
        #perface dictionary local indice to general indice
        l = 0
        first = True
        while not done:
            #getVertices
            if lines[l].find("mesh2") >=0 :
                localToglobal={}
                if lines[l].find("vertex_vectors") >= 0:
                    #new faces
                    #'mesh2 { vertex_vectors { 3, <6.8928928375,3.7201271057,-87.4298553467>,'
                    nvertex = int(lines[l].split("{")[2][0:2])
                    vertex=[[None,None,None],]*nvertex
                    for i in range(nvertex):
                        vliste = lines[l+i].split("<")[-1][:-2].split(",")
                        vertex[i] =[float(v) for v in vliste]
                    l=l+i+1
                if lines[l].find("normal_vectors") >= 0:
                    nnormal= int(lines[l].split("{")[1][0:2])
                    normal = [[None,None,None],]*nnormal
                    l = l +1
                    for i in range(nnormal):
                        nliste = lines[l+i].split("<")[-1][:-2].split(",")
                        normal[i] = [float(n) for n in nliste]
                    if self.debug:
                        print("normal",normal)
                    l=l+i+1
                if lines[l].find("texture_list") >= 0:
                    ncolor= int(lines[l].split("{")[1][0:2])
                    color = [[None,None,None],]*ncolor
                    for i in range(nnormal):
                        nliste = lines[l+i].split("<")[-1].split(">")[0].split(",")
                        color[i] = [float(n) for n in nliste]  
                    l=l+i+1
                if lines[l].find("face_indices") >= 0:
                    #local face order
                    nface = int(lines[l].split("{")[1][0:2])
                    local = lines[l].split("<")[-1].split(">")[0].split(",")
                    #localface = [int(f) for f in local]
                    l=l+1
                #ok now i should have the complete face, I can check
                if first :
                    normals.extend(normal)
                    vertices.extend(vertex)
                    faces.append([int(f) for f in local])
                    colors.extend(color)
                    first = False
                else :
                    #check if vertices already here
                    for i in range(3):
#                        try :
#                            iv=vertices.index(vertex[i])
#                        except :
#                            iv = -1
#                        if iv >= 0:
#                            #already exist do not add it, but keep the indice                            
#                            localToglobal[i] = iv
#                        else :
                        vertices.append(vertex[i])
                        normals.append(normal[i])
                        colors.append(color[i])
                        localToglobal[i] = len(vertices)-1
                    faces.append([localToglobal[int(f)] for f in local])
            if l == len(lines)-1 :
                done == True
                break
            if self.debug :
                print(l,lines[l])
        if self.debug:
            print(len(normals),normals[3])
        transformation = self.viewmat[9:12]-self.viewmat[12:15]
        vertices = numpy.array(vertices) - transformation
        return aGeom(vertices=vertices,faces=faces,
                        normals=numpy.array(normals),
                        colors=numpy.array(colors))
    def addHydrogen(self,name):
        self.cmd.do("h_add")

    def buildFragment(self,selection=None,fragment='cyclohexane'):
        #selection can come from epmv selection (AtomSet)-> can get molname+atomnumber
        if selection is None:
            return
        #check if slection is a H
        #create editable selection
        self.cmd.do("edit")
        print(selection)
        self.cmd.edit(selection,None,None,None,pkresi=0,pkbond=0)
        #build
        print(fragment,self.fragments[fragment])
        self.pymol.editor.attach_fragment('pk1',str(fragment),
                                          self.fragments[fragment][0],
                                          self.fragments[fragment][1],
                                          _self=self.cmd)
        #update?


#from ePMV.extension.pymolAdaptor import pymolAdaptor;y = pymolAdaptor();r=y.readMolecule("/Users/ludo/1crn.pdb");y.debug = 1;
#r1=y.displayExtrudedSS(r)