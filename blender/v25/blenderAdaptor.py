
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/blender/v25/blenderAdaptor.py is part of ePMV.

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
#############################################################################
#
# Author: Ludovic Autin
#
# Copyright: Ludovic Autin TSRI 2010
#
#
#############################################################################
import os
import sys

import ePMV
from ePMV.epmvAdaptor import epmvAdaptor
#from ePMV.blender import blenderHelper

import upy

import bpy
import mathutils


#blender_version = bpy.app.version
#if blender_version < (2,60,0):
#    from upy.blender.v257 import blenderHelper
#elif blender_version >= (2,60,0) and blender_version < (2,63,0): #2.62
#    from upy.blender.v262 import blenderHelper
#elif blender_version >= (2,63,0) : #2.62
#    from upy.blender.v263 import blenderHelper
#    

from MolKit.protein import ResidueSetSelector,Residue,Chain, Protein
from Pmv.pmvPalettes import AtomElements
from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
from Pmv.pmvPalettes import Shapely
from Pmv.pmvPalettes import SecondaryStructureType


#should we use prody to avoid all the issue with MolKit in python3.0

class blenderAdaptor(epmvAdaptor):
    def __init__(self,mv=None,debug=0,gui=False):
        self.soft = 'blender25'
        self.helper = upy.getHClass("blender25")()
        #overwrite 
#        self.setupMV = self.setupMV2
#        self.start = self.start2
#        self.addADTCommands = self.addADTCommands2
        epmvAdaptor.__init__(self,mv,host='blender25',debug=debug)

#        #scene and object helper function
        self._getCurrentScene = self.helper.getCurrentScene
##        self._addObjToGeom = self.helper.addObjToGeom
#        self._host_update = self.helper.update
##        self._parseObjectName = self.helper.parseObjectName
        self._getObjectName = self.helper.getName
        self._getObject = self.helper.getObject
        self._addObjectToScene = self.helper.addObjectToScene
        self._toggleDisplay = self.helper.toggleDisplay
        self._newEmpty = self.helper.newEmpty
#        self._deleteObject = self.helper.deleteObject 
#        #camera and lighting
        self._addCameraToScene = self.helper.addCameraToScene
        self._addLampToScene = self.helper.addLampToScene
#        #display helper function
#        self._editLines = self.helper.editLines
##        self._createBaseSphere = self.helper.createBaseSphere
##        self._instancesAtomsSphere = self.helper.instancesAtomsSphere
#        self._Tube = self.helper.Tube
        self._createsNmesh = self.helper.createsNmesh
        self._metaballs = self.helper.metaballs
        self._PointCloudObject = self.helper.PointCloudObject
#        #modify/update geom helper function
##        self._updateSphereMesh = self.helper.updateSphereMesh
        self._updateSphereObj = self.helper.updateSphereObj
#        self._updateSphereObjs = self.helper.updateSphereObjs
#        self._updateTubeMesh = self.helper.updateTubeMesh
        self._updateTubeObj = self.helper.updateTubeObj
#        self._updateMesh = self.helper.updateMesh
#        #color helper function
#        self._changeColor = self.helper.changeColor
#        self._checkChangeMaterial = self.helper.checkChangeMaterial
#        self._changeSticksColor = self.helper.changeSticksColor
#        self._checkChangeStickMaterial = self.helper.checkChangeStickMaterial
        #define the general function
        self._progressBar = None#Blender.Window.DrawProgressBar
        self.rep = "epmv"
        self.setupMaterials()
        self.matlist = self.helper.getAllMaterials()
        self.prevFrame = None
        self.callback = None
        if gui :
            self.createGUI()

    def start2(self,debug=0):
        """
        Initialise a PMV guiless session. Load specific command to PMV such as
        trajectory, or grid commands which are not automatically load in the 
        guiless session.
        
        @type  debug: int
        @param debug: debug mode, print verbose
        
        @rtype:   MolecularViewer
        @return:  a PMV object session.
        """  
        customizer = ePMV.__path__[0]+os.sep+"epmvrc.py"
#        print "customizer ",customizer
        #replace _pmvrc ?
        from PmvApp.Pmv import MolApp
        pmv = MolApp()
        if debug:
            pmv._stopOnError = True
        
        pmv.trapExceptions = False
#        mv = MoleculeViewer(logMode = 'overwrite', customizer=customizer, 
#                            master=None,title='pmv', withShell= 0,
#                            verbose=False, gui = False)
        return pmv

    def setupMV2(self):
        print ("setupMV",sys.version_info,sys.version_info < (3, 0))
        self.mv.lazyLoad('bondsCmds', package='PmvApp')
        self.mv.lazyLoad('fileCmds', package='PmvApp')
        self.mv.lazyLoad('displayCmds', package='PmvApp')
        self.mv.lazyLoad('editCmds', package='PmvApp')
        self.mv.displayLines.loadCommand()
        self.mv.lazyLoad("colorCmds", package="PmvApp")
        #pmv.setOnAddObjectCmd('Molecule', [pmv.buildBondsByDistance, pmv.displayLines])
        
        self.mv.lazyLoad("selectionCmds", package="PmvApp")
        #pmv.lazyLoad('msmsCmds', package='PmvApp')
        self.mv.lazyLoad('deleteCmds', package='PmvApp')
        #pmv.lazyLoad('secondaryStructureCmds', package='PmvApp')
#        self.mv.lazyLoad('displayHyperBallsCmds', package='PmvApp')
#        self.mv.lazyLoad('labelCmds', package='PmvApp')
#        self.mv.lazyLoad('displayHyperBallsCmds', package='PmvApp')

        self.mv.addCommand(BindGeomToMolecularFragment(), 'bindGeomToMolecularFragment', None)
        self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        self.mv.addCommand(PlayTrajectoryCommand(),'playTrajectory',None)
        self.mv.addCommand(addGridCommand(),'addGrid',None)
        self.mv.addCommand(readAnyGrid(),'readAny',None)
        self.mv.addCommand(IsocontourCommand(),'isoC',None)
        if sys.version_info < (3, 0):
            self.mv.browseCommands('colorCommands',package='ePMV.pmv_dev', topCommand=0)
        #self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        #self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        #define the listener
        if self.host is not None :
            self.mv.registerListener(DeleteGeomsEvent, self.updateGeom)
            self.mv.registerListener(AddGeomsEvent, self.updateGeom)
            self.mv.registerListener(EditGeomsEvent, self.updateGeom)
            self.mv.registerListener(AfterDeleteAtomsEvent, self.updateModel)
            self.mv.registerListener(BeforeDeleteMoleculesEvent,self.updateModel)
            self.mv.addCommand(loadMoleculeInHost(self),'_loadMol',None)            
            #self.mv.embedInto(self.host,debug=0)
            self.mv.embeded = True
        #compatibility with PMV
        self.mv.Grid3DReadAny = self.mv.readAny
        #mv.browseCommands('superimposeCommandsNew', package='Pmv', topCommand=0)
        self.mv.userpref['Read molecules as']['value']='conformations'
        self.mv.setUserPreference(('Read molecules as', 'conformations',), log=0)
        self.mv.setUserPreference(('Number of Undo', '0',), redraw=0, log=1)
        self.mv.setUserPreference(('Save Perspective on Exit', 'no',), log=0)
        self.mv.setUserPreference(('Transformation Logging', 'no',), log=0) 
        #should add some user preferece and be able to save it       
        #recentFiles Folder
#        rcFile = self.mv.rcFolder
#        if rcFile:
#            rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
#            self.mv.recentFiles = RecentFiles(self.mv, None, filePath=rcFile,index=0)
#        else :
#            print("no rcFolder??")
#        
        #this  create mv.hostapp which handle server/client and log event system
        #NOTE : need to test it in the latest version
#        if not self.useLog : 
#            self.mv.hostApp.driver.useEvent = True
        self.mv.iTraj={}
        
        self.funcColor = [self.mv.colorByAtomType,
                          self.mv.colorAtomsUsingDG,
                          self.mv.colorByResidueType,
                          self.mv.colorResiduesUsingShapely,
                          self.mv.colorBySecondaryStructure,
                          self.mv.colorByChains,
                          self.mv.colorByDomains,
                          self.mv.color,
                          self.mv.colorByProperty]
        self.fTypeToFc = {"ByAtom":0,"AtomsU":1,"ByResi":2,"Residu":3,
                          "BySeco":4,"ByChai":5,"ByDoma":6,"":7,
                          "ByPropN":8,"ByPropT":9,"ByPropS":10}
        self.mv.host = self.host
#        self.mv.selectionLevel = Atom
#        mv.hostApp.driver.bicyl = self.bicyl

    def addADTCommands2(self,):
        pass
        
    def synchronize(self):
        if self.synchro_timeline :
            self.synchronize_timeline()
        else :
            if self.callback != None :
                bpy.app.handlers.frame_change_pre.pop(self.callback)
                
    def synchronize_timeline(self): 
        def callback(scene):
            traj = self.gui.current_traj
            print("Frame Change", scene.frame_current)
            frame = scene.frame_current
            st,ft=self.synchro_ratio
            doit = True
            if (self.prevFrame != None) :
                if (frame == self.prevFrame) :
                    doit = False
            if (frame % ft) == 0 and doit:   
                step = frame * st
                self.updateData(traj,step)
            #self.updateData(traj,step)
        self.callback = callback
        bpy.app.handlers.frame_change_pre.append(self.callback)
            
    def _resetProgressBar(self,max):
        pass

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
#        return None
        sc=self.helper.getCurrentScene()
        if shape is None :
            res = bpy.ops.curve.primitive_bezier_circle_add()
            shape = bpy.context.object
            shape.name = name+"Circle"
            self.helper.scaleObj(shape,0.3)
#            shape = sc.objects.new(self.helper.bezCircle(0.3,name+"Circle"))
        if spline is None :
            obSpline,spline = self.helper.spline(name,coords,extrude_obj=shape,scene=sc)
        if parent is not None :
            parent=self.helper.getObject(parent)
            obSpline.parent = parent
        return obSpline

    def _createBaseSphere(self,name="",quality=0,radius=None,cpkRad=0.0,
                         scale=1.0,scene=None,parent=None):
        #name = mol.name+"_b_cpk"
        #AtomElements.keys() ['A', 'C', 'H', 'CA', 'O', 'N', 'P', 'S']
        scene = self.helper.getCurrentScene()
        #default the values.
        QualitySph={"0":[15,15],"1":[5,5],"2":[10,10],"3":[15,15],
                    "4":[20,20],"5":[25,25],"6":[32,32]} 
        segments=quality*2
        rings=quality*5
        if quality == 0 : 
            segments = 15#25
            rings = 15#25
        iMe={}
        n=name.split("_")[2] #cpk or balls
        basesphere=self.helper.getObject("basesphere")
        #print "basesphere ",basesphere
        if basesphere is None : 
            print ("basesphere")
            basesphere,meshsphere = self.helper.Sphere("basesphere",res=segments)
            self.helper.toggleDisplay(basesphere,display=False)
        if scene is not None : iObj=[]
        for atn in list(self.AtmRadi.keys()):
            rad=float(self.AtmRadi[atn])#float(cpkRad)+float(AtmRadi[atn])*float(scale)
            iMe[atn]= self.helper.getMesh("m_"+name+'_'+atn)
            if iMe[atn] is None :
                iMe[atn],me=self.helper.Sphere(name+'_'+atn,
                                                     res=segments,
                                                     mat = atn)
                Smatrix=mathutils.Matrix.Scale(float(rad)*2., 4)
#                bpy.ops.object.mode_set(mode='EDIT')
#                #Select all the vertices
#                print ("basesphere scale")
#                bpy.ops.mesh.select_all(action='SELECT')
#                print ("basesphere scale",float(rad))
#                bpy.context.scene.update()
#                bpy.ops.transform.resize(value=(float(rad),float(rad),float(rad)))
#                print ("basesphere scale")
#                bpy.ops.object.mode_set(mode='OBJECT')
                print ("basesphere scale ok")
                #iMe[atn].matrix_world *= Smatrix
                me.transform(Smatrix)
                if scene != None : 
                    iObj.append(iMe[atn])
                    print ("toggle it",iMe[atn])
                    self.helper.toggleDisplay(iMe[atn],display=False)
        cpk=self.helper.getObject(name)
        if scene !=  None and cpk is None : 
            cpk = self.helper.newEmpty(name)
            print ("cpk ",name)
#            self.helper.addObjectToScene(scene,cpk,parent=parent)
            self.helper.toggleDisplay(cpk,display=False)
            print ("toggle")
            self.helper.reParent(iObj,cpk)
        print ('done')
        return iMe

#    def _instancesAtomsSphere(self,name,x,iMe,scn,mat=None, scale=1.0,Res=32,R=None,
#                             join=0,geom=None,pb=False):
#        if scn == None :
#            scn=self.helper.getCurrentScene()
#        objs=[]
#        mol = x[0].getParentOfType(Protein)
#        n='S'
#        nn="cpk"
#        if name.find('balls') != (-1) : 
#            n='B'
#            nn="balls"
#        if geom is not None : 
#            coords=geom.getVertices()
#        else : 
#            coords = x.coords
#        hiera = 'default'
#        #what about chain...
##        parent=self.findatmParentHierarchie(x[0],n,hiera)
#        for c in mol.chains:
#            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name+"_"+nn]) 
#            obj=[]
#            oneparent = True 
#            atoms = c.residues.atoms
##            parent=self.findatmParentHierarchie(atoms[0],n,hiera)
#            for j in range(len(atoms.coords)):
#                at=atoms[j]
#                atN=at.name
#                if atN[0] not in list(AtomElements.keys()) : atN="A"
#                #print atN
#                #fullname = at.full_name()
#                atC=atoms.coords[j]#at._coords[0]
#                #print atC, fullname,at.full_name()
#                mesh=iMe[atN[0]]
#                if type(mesh) == str :
#                    mesh=self.helper.getMesh(mesh)
#                atfname = self.atomNameRule(at,n)
#                #at.full_name().replace("'","b")+"n"+str(at.number)
#                #there is a string lenght limitation in blender object name...this is too long
#                #print "fullname ",atfname
#                #OBJ=scn.objects.new(mesh,atfname)
#                res = bpy.ops.object.add(type='MESH',location=atC)
#                OBJ = bpy.context.object
#                OBJ.name = atfname
#                OBJ.data = mesh
#                #print "obj ",OBJ.name
##                self.helper.translateObj(OBJ,atC)
#                self.helper.setOneMaterial(OBJ,self.helper.getMaterial(atN[0]),objmode =True)
##                OBJ.colbits = 1<<0
##                p = findatmParentHierarchie(at,n,hiera)
##                if parent != p : 
##                    p.makeParent([OBJ])
##                    oneparent = False
#                self.helper.toggleDisplay(OBJ,False)
#                obj.append(OBJ)
#                if pb and (j%50) == 0:
#                    progress = float(j) / len(coords)
#                    #Blender.Window.DrawProgressBar(progress, 'creating '+name+' spheres')
#            if oneparent :
#                self.helper.reParent(obj,parent)#.makeParent(obj)
#            objs.extend(obj)
##        if join==1 : 
##            obj[0].join(obj[1:])
##            for ind in range(1,len(obj)):
##                scn.unlink(obj[ind])
##            obj[0].setName(name)
#        return  objs

    def _changeColor(self,geom,colors,perVertex=True,perObjectmat=None,pb=False):
        if hasattr(geom,'mesh'):
            objToColor = geom.mesh
        elif hasattr(geom,'obj'):
            objToColor = geom.obj
        else :
            if type(geom) is str :
                objToColor = self.helper.getObject(geom)
            else :
                objToColor = geom                
        if objToColor is None :
            return
        self.helper.changeColor(objToColor,colors,perVertex=perVertex,
                         perObjectmat=perObjectmat,pb=pb)

    def _armature(self,name,atomset,coords=None,root=None,scn=None):
        names = None
        if coords is not None :
            c = coords    
        else :
            c = atomset.coords
            names = [x.full_name().replace(":","_") for x in atomset]
        object,bones=self.helper.armature(name,c,listeName=names,
                                          root=root,scn=scn)
        return object,bones
        
    def atoms_armature(self,name,atoms,scn):
        return self.armature(name,atoms.coords,scn=scn)

    def bond_armature(self,name,bonds,scn):
        #need the bonds coordinates
        pass
    
#    def updateTubeObjsFromGeom(self,g):
#        if not hasattr(g,'obj') : return
#        newpoints=g.getVertices()
#        newfaces=g.getFaces()
#        self.updateTubeObjs(g.obj,newpoints,newfaces)

    def updateMolAtomCoordBones(self,mol,index=-1):
        #problem, how to know the armature mode ?
        vt = []
        arm_obj = mol.geomContainer.geoms["armature"][0]
        arm_mat= arm_obj.matrix_world
        arm_data = arm_obj.pose #getData()
        bones = list(arm_data.bones.values())# mol.geomContainer.geoms["armature"][1]       
        #one bones = 2 atoms => head and tail
        #this give the initial position#*eb.matrix['ARMATURESPACE']
        vt = [self.helper.ToVec(eb.head*arm_mat) for eb in bones]
        vt.append(self.helper.ToVec(bones[-1].tail*arm_mat)) #self.helper.getBoneMatrix(bones[-1])))*bones[-1].matrix['ARMATURESPACE']
#        vt = [self.helper.ToVec(eb.head['ARMATURESPACE']) for eb in bones]
#        vt.append(self.helper.ToVec(bones[-1].tail['ARMATURESPACE'])) #self.helper.getBoneMatrix(bones[-1])))*bones[-1].matrix['ARMATURESPACE']
#        #need to apply the matrix to input coordinate ?
#        vt = [self.helper.ToVec(self.helper.getBoneMatrix(j,arm_mat=arm_mat).translationPart()) \
#                            for j in bones]
        print(vt[0])
        return vt
    
    def updateMolAtomCoordSpline(self,mol,index=-1):
        #problem, theses are only CA. TODOs
        v=[]
        vt = []
        vts=[]
    #    mesh = mol.geomContainer.geoms['lines'].obj
        for ch in mol.chains:
            name=mol.name+"_"+ch.name+"spline"
            spline = self.helper.getObject(name)
            curvedata = spline.data
            mat = spline.matrix_world
            #curve_data can have different curve nurb           
            for curnurb in curvedata:
                vt = [self.helper.ToVec(point.vec[1]) for point in curnurb] #a point is a BezTriple with a list of the 3 points [ handle, knot, handle ]
                vts.extend(vt)
            v.append(vts)
        return v
        
    def updateMolAtomCoordLines(self,mol,index=-1):
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        vts=[]
        for ch in mol.chains:
            vt = []
        #    mesh = mol.geomContainer.geoms['lines'].obj
            print(ch.full_name()+'_line')
            ob = mol.geomContainer.geoms[ch.full_name()+'_line'][0] #ob,mesh
            mesh = mol.geomContainer.geoms[ch.full_name()+'_line'][1] 
            print(mesh)
            if mesh is None :
                mesh = self.helper.getObject(ch.full_name()+'_line')
            print(mesh)
            points = self.helper.getMeshVertices(ob)#transform?
            #matr= mesh.GetMg()
            mmat = ob.matrix_world #Py_Matrix (WRAPPED DATA)
            mat = mmat #self.helper.m2matrix(mmat)
            print(mat,points[0])
            import numpy
            print(numpy.array(mat))
            vt = self.helper.ApplyMatrix(points,numpy.array(mat).transpose())
            #vt=points#[self.helper.vc4d(x*matr) for x in points]
            vts.extend(vt)
        #vt = map(lambda x,m=matr: vc4d(x*m),points)
        #these are the cpk, should we update them here?
        if hasattr(mol.geomContainer.geoms['cpk'],'obj'):
            sph = mol.geomContainer.geoms['cpk'].obj
            #each have to be translate
            [self.helper.setTranslationObj(x,p) for x,p in zip(sph,vts)]
            #map(lambda x,p:x.SetAbsPos(p),sph,points)
#            masterCPK=sph[0].GetUp()
#            masterCPK.SetMg(matr)
        return vts#updateMolAtomCoordCPK(mol,index=index)

    def _editLines(self,molecules,atomSets):
        scn = self.helper.getCurrentScene()
        for mol, atms in zip(molecules, atomSets):
            #check if line exist
            for ch in mol.chains:
                parent = self.helper.getObject(ch.full_name())
                lines = self.helper.getObject(ch.full_name()+'_line')
                bonds, atnobnd = ch.residues.atoms.bonds
                indices = [(x.atom1._bndIndex_,
                                             x.atom2._bndIndex_) for x in bonds]                
                if lines == None :
                    lines = self.helper.createsNmesh(ch.full_name()+'_line',ch.residues.atoms.coords,
                                         None,indices,parent=parent)
                    #self.helper.addObjectToScene(scn,lines[0]	,parent=parent)
                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
                    #addObjToGeom(lines,mol.geomContainer.geoms['lines'])
                else : #need to update
                    mods = lines.modifiers
                    if mods:
                        return
                    self.helper.updatePoly(lines,vertices=ch.residues.atoms.coords,
                                               faces = indices)
#                    self._updateLines(lines, chains=ch)

    def createGUI(self):
        from ePMV.epmvGui import epmvGui
        self.gui = epmvGui(epmv=self,rep='epmv')

