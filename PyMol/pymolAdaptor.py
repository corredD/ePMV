
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/PyMol/pymolAdaptor.py is part of ePMV.

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
Created on Tue Feb 15 10:07:51 2011

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import numpy

class pymolGeom:
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
        

class pymolAdaptor:
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
        self.Mols = {}
        self.pymol = pymol
        self.debug = debug
        self.viewmat = None#numpy.array(self.cmd.get_view(quiet=1))
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
    
    def readMolecule(self,filename,name=None):
        if name is None :
            name = filename.split('/')[-1].split('.')[0]
        self.cmd.load(filename,name)
        self.Mols[name]={}
        return name

    def toggleFancy(self,fancyH):
        val = int(fancyH)
        self.cmd.do("set cartoon_fancy_helices, "+str(val))

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
        geom = self.parsePOVoptimized(name,rep="cartoon")
        self.Mols[name]["ss"] = geom
#        self.cmd.do("set light_count, 2")
        return geom
    
    def parsePOV(self,name,rep="cartoon"):
        #undisplay everything
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
        while not done:
            #getVertices
            if lines[l].find("mesh2") >=0 :
                localToglobal={}
                if lines[l].find("vertex_vectors") >= 0:
                    #new faces
                    #'mesh2 { vertex_vectors { 3, <6.8928928375,3.7201271057,-87.4298553467>,'
                    nvertex = int(lines[l].split("{")[2][0:2])
                    #vertex=numpy.zeros((nvertex,3))
                    for i in range(nvertex):
                        vliste = lines[l+i].split("<")[-1][:-2].split(",")
                        vertices.append( [float(v) for v in vliste])#vertex[i] =
                        localToglobal[i] = len(vertices)-1
        #            vertices.extend(vertex)
                    l=l+i+1
                if lines[l].find("normal_vectors") >= 0:
                    nnormal= int(lines[l].split("{")[1][0:2])
        #            normal = numpy.zeros((nnormal,3))
                    l = l +1
                    for i in range(nnormal):
                        nliste = lines[l+i].split("<")[-1][:-2].split(",")
        #                normal[i] = [float(n) for n in nliste] 
                        normals.append([float(n) for n in nliste] )
        #            normals.extend(normal)
                    l=l+i+1
                if lines[l].find("texture_list") >= 0:
                    ncolor= int(lines[l].split("{")[1][0:2])
        #            color = numpy.zeros((nnormal,3))
                    for i in range(nnormal):
                        nliste = lines[l+i].split("<")[-1].split(">")[0].split(",")
        #                color[i] = [float(n) for n in nliste]  
                        colors.append([float(n) for n in nliste]  )
        #            colors.extend(color)
                    l=l+i+1
                if lines[l].find("face_indices") >= 0:
                    #local face order
                    nface = int(lines[l].split("{")[1][0:2])
                    local = lines[l].split("<")[-1].split(">")[0].split(",")
                    #face = [localToglobal.index(int(f)) for f in local]
                    face = [localToglobal[int(f)] for f in local]
                    faces.append(face)
                    l=l+1
            if l == len(lines)-1 :
                done == True
                break
            print(l,lines[l])
        normals=numpy.array(normals)
        colors=numpy.array(colors)
        transformation = self.viewmat[9:12]-self.viewmat[12:15]
        vertices = numpy.array(vertices) - transformation
        return pymolGeom(vertices=numpy.array(vertices),faces=faces,
                        normals=numpy.array(normals),
                        colors=numpy.array(colors),pov=pov)
                
    def parsePOVoptimized(self,name,rep="cartoon"):
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
        return pymolGeom(vertices=vertices,faces=faces,
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


try :
    from upy import uiadaptor
except :
    uiadpator = None
class pymolGui(uiadaptor):
    def setup(self,sub=False,pym=None,epmv=None,id=None):
        self.subdialog = sub
        self.title = "PyMol"
        self.epmv = epmv
        self.pym = pym
        if self.subdialog:
            self.block = True
        witdh=350
        self.w = 200
        self.h = 200
        if id is not None :
            id=id
        else:
            id = self.bid
        #define the button here
        self.LABELS={}        
        self.BTN={}
        self.COMBO={}
        self.CHKBOX={}
        if self.epmv is not None : #work on the current_mol

            self.LABELS["header"] = self._addElemt(label="Pymol plugin for ePMV",width=120)
            self.LABELS["current"] = self._addElemt(label="apply on the current epmv mol",width=120)
            self.LABELS["buildF"] = self._addElemt(label="choose the fragment",width=120)
            

            self.BTN["ss"] = self._addElemt(name="show cartoon",width=50,height=10,
                              label = 'show ribbon cartoon',
                         action=self.dsCartoon,type="button")
            self.BTN["buildF"] = self._addElemt(name="buildF",width=150,height=10,
                              label = 'build fragment on current picked H',
                         action=self.buildF,type="button")
            self.BTN["ok"] = self._addElemt(name="Ok",width=50,height=10,
                         action=self.cancel,type="button")
            
            self.CHKBOX["fancyH"] = self._addElemt(name="fancyH",width=80,height=10,
                                              action=self.dsCartoon,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
        else : #need a load molecule button
            pass
        #common widget
        self.cartoon=["color SS","publication"]
        self._cartoon=self.addVariable("int",1)
        self.fragment=list(self.pym.fragments.keys())
        self._fragment=self.addVariable("int",1)
        
        self.COMBO["ss"] = self._addElemt(name="ssStyle",value=self.cartoon,
                                width=60,height=10,action=None,
                                variable=self._cartoon,
                                type="pullMenu")
        self.COMBO["buildF"] = self._addElemt(name="buildF",value=self.fragment,
                                width=60,height=10,action=None,
                                variable=self._fragment,
                                type="pullMenu")                        
 
        #then define the layout
        self.setupLayout()
#        self.restorePreferences()
        return True

    def setupLayout(self):
        self._layout = []
        self._layout.append([self.LABELS["header"],])
        self._layout.append([self.LABELS["current"],])
        self._layout.append([self.COMBO["ss"],self.CHKBOX["fancyH"]])
        self._layout.append([self.BTN["ss"],])
        self._layout.append([self.LABELS["buildF"],self.COMBO["buildF"]])
        self._layout.append([self.BTN["buildF"],])
        self._layout.append([self.BTN["ok"],])
        
    def CreateLayout(self):
        self._createLayout()
        return True

    def cancel(self,*args):
        self.close()

    def toggleFancy(self,*args):
        val = self.getBool(self.CHKBOX["fancyH"])
        self.pym.toggleFancy(val)

    def dsCartoon(self,*args):
        if self.epmv is not None :
            mname,mol,sel,selection = self.epmv.gui.getDsInfo()
            parent=mol.geomContainer.masterGeom.obj
            #check if mol is already loaded in pymol
            name = mol.name
            if mol.name not in list(self.pym.Mols.keys()):
                name = self.pym.readMolecule(mol.parser.filename,name=mol.name)
        else : #get the current mol
            parent =None
            name ="test"
        #ok now get the option
        fancy = self.getBool(self.CHKBOX["fancyH"])
        style = self.cartoon[self.getLong(self.COMBO["ss"])]
        geom = self.pym.displayExtrudedSS(name,fancyH=fancy,color=style)
        cartoonObj = self.epmv.helper.getObject(name+"cartoon")
        if cartoonObj is None :
            obj=self.epmv.helper.createsNmesh(name+"cartoon",geom.vertices,
                                          geom.normals,geom.faces,proxyCol=True)
            self.epmv.helper.addObjectToScene(self.epmv.helper.getCurrentScene(),
                                          obj[0],parent=parent)
            cartoonObj = obj[0]
        else :
            self.epmv.helper.updateMesh(cartoonObj,vertices=geom.vertices,#geom.normals
                                          faces=geom.faces)
        self.epmv.helper.alignNormal(cartoonObj)#obj[1])
        self.epmv.helper.changeColor(cartoonObj,geom.colors,pb=False)#,proxyObject=True)

    def buildF(self,*args):
        #get the fragment
        fragment = self.fragment[self.getLong(self.COMBO["buildF"])]
        #get the selection
        listeAtomsNumber=[]
        if self.epmv is not None :
            mname,mol,sel,selection = self.epmv.gui.getDsInfo()
            parent=mol.geomContainer.masterGeom.obj
            #check if mol is already loaded in pymol
            name = mol.name
            if mol.name not in list(self.pym.Mols.keys()):
                name = self.pym.readMolecule(mol.parser.filename,name=mol.name)
            listeAtomsNumber = [(atm.number+1) for atm in selection]
        else : #get the current mol
            parent =None
            name ="test"
        for atmNb in listeAtomsNumber:
            sel = "(%s`%d)" % (name,atmNb)
            self.pym.buildFragment(selection=sel,fragment=fragment)
        self.pym.cmd.save("/Users/ludo/"+name+"_pym.pdb")
        #what should I do, dump the pdb? update epmv mol? delete / load the new molecule

    def Command(self,*args):
#        print args
        self._command(args)
        return True


    