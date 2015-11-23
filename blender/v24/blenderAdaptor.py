
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/blender/v24/blenderAdaptor.py is part of ePMV.

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
#############################################################################
#
# Author: Ludovic Autin
#
# Copyright: Ludovic Autin TSRI 2010
#
#
#############################################################################
import os

import ePMV
from ePMV.epmvAdaptor import epmvAdaptor
from upy.blender.v249 import blenderHelper

import Blender
from Blender import Material

from MolKit.protein import ResidueSetSelector,Residue,Chain, Protein
from Pmv.pmvPalettes import AtomElements
from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
from Pmv.pmvPalettes import Shapely
from Pmv.pmvPalettes import SecondaryStructureType


class blenderAdaptor(epmvAdaptor):
    def __init__(self,mv=None,debug=0,gui=False):
        self.soft = 'blender24'
        self.helper = blenderHelper.blenderHelper()
#        print ("blenderAdaptor",self.helper)
        epmvAdaptor.__init__(self,mv,host='blender24',debug=debug)

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
        self._progressBar = Blender.Window.DrawProgressBar
        self.rep = "epmv"
        self.setupMaterials()
        self.matlist = self.helper.getAllMaterials()
        if gui :
            self.createGUI()

    def synchronize(self):
        prefdir = Blender.Get('uscriptsdir')
        if prefdir is None:
            prefdir = Blender.Get('scriptsdir')        
        self.helper.addTextFile(name="epmv_synchro",
                                file=prefdir+os.sep+"epmv_blender_update.py")
        scene = self.helper.getCurrentScene()
        #should load the script for scene update...
        if self.synchro_realtime :
            if not hasattr(self,"epmv_synchro") or not self.epmv_synchro:
                scene.addScriptLink("epmv_synchro", "FrameChanged")
                self.epmv_synchro = True
        else :
            scene.clearScriptLinks()
            self.epmv_synchro = False
        #Parameters:
        # * text (string) - the name of an existing Blender Text.
        # * event (string) - "FrameChanged", "OnLoad", "OnSave", "Redraw" or "Render".
        #sc.clearScriptLinks(links=None)
        
    def _resetProgressBar(self,max=None):
        pass

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self.helper.getCurrentScene()
        if shape is None :
            shape = sc.objects.new(self.helper.bezCircle(0.3,name+"Circle"))
        if spline is None :
            obSpline,spline = self.helper.spline(name,coords,extrude_obj=shape,scene=sc)
        if parent is not None :
            parent=self.helper.getObject(parent)
            parent.makeParent([obSpline])
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
            basesphere,meshsphere = self.helper.Sphere("basesphere",res=segments)
            self.helper.toggleDisplay(basesphere,display=False)
        if scene is not None : iObj=[]
        for atn in  list(self.AtmRadi.keys()):
            rad=float(self.AtmRadi[atn])#float(cpkRad)+float(AtmRadi[atn])*float(scale)
#            iMe[atn]= self.helper.getMesh("mesh_"+name+'_'+atn)
            iMe[atn]= self.helper.getObject( name+'_'+atn )
            if iMe[atn] is None :
                iMe[atn],me=self.helper.Sphere(name+'_'+atn,
                                                     res=segments,
                                                     mat = atn)
                Smatrix=Blender.Mathutils.ScaleMatrix(float(rad)*2., 4)
                me.transform(Smatrix)
                if scene != None : 
                    iObj.append(iMe[atn])
                    self.helper.toggleDisplay(iMe[atn],display=False)
        cpk=self.helper.getObject(name)
        if scene !=  None and cpk is None : 
            cpk = self.helper.newEmpty(name)
            self.helper.addObjectToScene(scene,cpk,parent=parent)
            self.helper.toggleDisplay(cpk,display=False)
            self.helper.reParent(iObj,cpk)
            #print 'iobj ',len(iObj)
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
#                OBJ=scn.objects.new(mesh,atfname)
#                #print "obj ",OBJ.name
#                self.helper.translateObj(OBJ,atC)
#                OBJ.setMaterials([Blender.Material.Get(atN[0])])
#                OBJ.colbits = 1<<0
##                p = findatmParentHierarchie(at,n,hiera)
##                if parent != p : 
##                    p.makeParent([OBJ])
##                    oneparent = False
#                self.helper.toggleDisplay(OBJ,False)
#                obj.append(OBJ)
#                if pb and (j%50) == 0:
#                    progress = float(j) / len(coords)
#                    Blender.Window.DrawProgressBar(progress, 'creating '+name+' spheres')
#            if oneparent :
#                parent.makeParent(obj)
#            objs.extend(obj)
#        if join==1 : 
#            obj[0].join(obj[1:])
#            for ind in range(1,len(obj)):
#                scn.unlink(obj[ind])
#            obj[0].setName(name)
#        return  objs

    def _changeColor(self,geom,colors,perVertex=True,perObjectmat=None,pb=False):
        print(geom)
        if hasattr(geom,'mesh'):
            objToColor = geom.mesh
        elif hasattr(geom,'obj'):
            objToColor = geom.obj
        else :    
            if type(geom) is str :
                objToColor = self.helper.getObject(geom)
            else :
                objToColor = geom                
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
    
    def updateTubeObjsFromGeom(self,g):
        if not hasattr(g,'obj') : return
        newpoints=g.getVertices()
        newfaces=g.getFaces()
        self.updateTubeObjs(g.obj,newpoints,newfaces)

    def updateMolAtomCoordBones(self,mol,index=-1):
        #problem, how to know the armature mode ?
        vt = []
        arm_obj = mol.geomContainer.geoms["armature"][0]
        arm_mat= arm_obj.matrixWorld
        arm_data = arm_obj.getPose() #getData()
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
            mat = spline.getMatrix()
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
            mmat = ob.getMatrix() #Py_Matrix (WRAPPED DATA)
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
        for mol, atms, in map(None, molecules, atomSets):
            #check if line exist
            for ch in mol.chains:
                parent = self.helper.getObject(ch.full_name())
                lines = self.helper.getObject(ch.full_name()+'_line')
                if lines == None :
                    bonds, atnobnd = ch.residues.atoms.bonds
                    indices = [(x.atom1._bndIndex_,
                                             x.atom2._bndIndex_) for x in bonds]
                    
                    lines = self.helper.createsNmesh(ch.full_name()+'_line',ch.residues.atoms.coords,
                                         None,indices)
                    self.helper.addObjectToScene(scn,lines[0]	,parent=parent)
                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
                    #addObjToGeom(lines,mol.geomContainer.geoms['lines'])
                else : #need to update
                    mods = lines.modifiers
                    if mods:
                        return
                    self.helper.updatePoly(lines,vertices=ch.residues.atoms.coords)
#                    self._updateLines(lines, chains=ch)

    def createGUI(self):
        from ePMV.epmvGui import epmvGui
        self.gui = epmvGui(epmv=self,rep='epmv')

