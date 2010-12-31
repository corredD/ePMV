#############################################################################
#
# Author: Ludovic Autin
#
# Copyright: Ludovic Autin TSRI 2010
#
#
#############################################################################
import ePMV
from ePMV.epmvAdaptor import epmvAdaptor
from ePMV.epmvGui import epmvGui
#from ePMV.blender import blenderHelper
from pyubic.blender import blenderHelper

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
        epmvAdaptor.__init__(self,mv,host='blender',debug=debug)
        self.soft = 'blender'
        self.helper = blenderHelper.blenderHelper()
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
#        self._PointCloudObject = self.helper.PointCloudObject
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
            
    def _resetProgressBar(self,max):
        pass

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self.helper.getCurrentScene()
        if shape is None :
            shape = sc.objects.new(self.helper.bezCircle(0.3,name+"Circle"))
        if spline is None :
            obSpline,spline = self.helper.spline(name,coords,extrude_obj=shape,scene=sc)
        if parent is not None :
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
            meshsphere,basesphere=self.helper.Sphere("basesphere",res=segments)
            self.helper.toggleDisplay(basesphere,display=False)
        if scene is not None : iObj=[]
        for atn in  self.AtmRadi.keys():
            rad=float(self.AtmRadi[atn])#float(cpkRad)+float(AtmRadi[atn])*float(scale)
            iMe[atn]= self.helper.getMesh("mesh_"+name+'_'+atn)
            if iMe[atn] is None :
                iMe[atn],ob=self.helper.Sphere(name+'_'+atn,
                                                     res=segments,
                                                     mat = atn)
                Smatrix=Blender.Mathutils.ScaleMatrix(float(rad)*2., 4)
                iMe[atn].transform(Smatrix)
                if scene != None : 
                    iObj.append(ob)
                    self.helper.toggleDisplay(ob,display=False)
        cpk=self.helper.getObject(name)
        if scene !=  None and cpk is None : 
            cpk = self.helper.newEmpty(name)
            self.helper.addObjectToScene(scene,cpk,parent=parent)
            self.helper.toggleDisplay(cpk,display=False)
            self.helper.reParent(iObj,cpk)
            #print 'iobj ',len(iObj)
        return iMe

    def _instancesAtomsSphere(self,name,x,iMe,scn,mat=None, scale=1.0,Res=32,R=None,
                             join=0,geom=None,pb=False):
        if scn == None :
            scn=self.helper.getCurrentScene()
        objs=[]
        mol = x[0].getParentOfType(Protein)
        n='S'
        if name.find('balls') != (-1) : n='B'
        if geom is not None : 
            coords=geom.getVertices()
        else : 
            coords = x.coords
        hiera = 'default'
        #what about chain...
        parent=self.findatmParentHierarchie(x[0],n,hiera)
        for c in mol.chains:
            obj=[]
            oneparent = True 
            atoms = c.residues.atoms
            parent=self.findatmParentHierarchie(atoms[0],n,hiera)
            for j in xrange(len(atoms.coords)):
                at=atoms[j]
                atN=at.name
                if atN[0] not in AtomElements.keys() : atN="A"
                #print atN
                #fullname = at.full_name()
                atC=atoms.coords[j]#at._coords[0]
                #print atC, fullname,at.full_name()
                mesh=iMe[atN[0]]
                if type(mesh) == str :
                    mesh=self.helper.getMesh(mesh)
                atfname = at.full_name()
                #there is a string lenght limitation in blender object name...
                #print "fullname ",atfname
                OBJ=scn.objects.new(mesh,n+"_"+atfname)
                #print "obj ",OBJ.name
                self.helper.translateObj(OBJ,atC)
                OBJ.setMaterials([Blender.Material.Get(atN[0])])
                OBJ.colbits = 1<<0
#                p = findatmParentHierarchie(at,n,hiera)
#                if parent != p : 
#                    p.makeParent([OBJ])
#                    oneparent = False
                self.helper.toggleDisplay(OBJ,False)
                obj.append(OBJ)
                if pb and (j%50) == 0:
                    progress = float(j) / len(coords)
                    Blender.Window.DrawProgressBar(progress, 'creating '+name+' spheres')
            if oneparent :
                parent.makeParent(obj)
            objs.extend(obj)
        if join==1 : 
            obj[0].join(obj[1:])
            for ind in range(1,len(obj)):
                scn.unlink(obj[ind])
            obj[0].setName(name)
        return  objs

    def _changeColor(self,geom,colors,perVertex=True,perObjectmat=None,pb=False):
        self.helper.changeColor(geom.mesh,colors,perVertex=perVertex,
                         perObjectmat=perObjectmat,pb=pb)

    def _armature(self,name, atomset):
        self.helper.armature(name, atomset.coords)
        
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
        #problem, theses are only CA
        vt = []
        bones = mol.geomContainer.geoms["armature"][1]
        vt = [self.helper.vc4d(j.GetMg().off) for j in bones]
#        for join in bones:
#            pos=join.GetMg().off
#            vt.append(self.helper.vc4d(pos))
        print vt[0]
        return vt
    
    def updateMolAtomCoordSpline(self,mol,index=-1):
        #problem, theses are only CA
        vt = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        name=mol.name+"_"+mol.chains[0].name+"spline"
        spline = self.helper.getCurrentScene().SearchObject(name)
        points = spline.GetAllPoints()
    #    matr= mesh.GetMg()
    #    vt = map(lambda x,m=matr: vc4d(x),points)
        vt = [self.helper.vc4d(x) for x in points]
        return vt
        
    def updateMolAtomCoordLines(self,mol,index=-1):
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        vt = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        mesh = mol.geomContainer.geoms[mol.chains[0].full_name()+'_line'][0]
        points = mesh.GetAllPoints()
        matr= mesh.GetMg()
        vt=[self.helper.vc4d(x*matr) for x in points]
        #vt = map(lambda x,m=matr: vc4d(x*m),points)
        #these are the cpk
        if hasattr(mol.geomContainer.geoms['cpk'],'obj'):
            sph = mol.geomContainer.geoms['cpk'].obj
            #each have to be translate
            [x.SetAbsPos(p) for x,p in zip(sph,points)]
            #map(lambda x,p:x.SetAbsPos(p),sph,points)
            masterCPK=sph[0].GetUp()
            masterCPK.SetMg(matr)
        return vt#updateMolAtomCoordCPK(mol,index=index)
        
    def updateMolAtomCoordCPK(self,mol,index=-1):
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        vt = []
        sph = mol.geomContainer.geoms['cpk'].obj
        for name in sph:
            o = self.helper.getObject(name)
            pos=o.GetMg().off
    #        pos=o.GetAbsPos()
            vt.append(vc4d(pos))
        print vt[0]
        return vt

    def createGUI(self):
        self.gui = epmvGui(epmv=self,rep='epmv')

