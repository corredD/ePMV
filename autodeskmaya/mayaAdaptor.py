#############################################################################
#
# Author: Ludovic Autin
#
# Copyright: Ludovic Autin TSRI 2010
#
#
#############################################################################

from ePMV.epmvAdaptor import epmvAdaptor
from pyubic.autodeskmaya import helperMaya
import maya
from maya import OpenMaya
from maya import OpenMayaAnim as oma
from maya import cmds

from MolKit.protein import ResidueSetSelector,Residue,Chain, Protein
from Pmv.pmvPalettes import AtomElements
from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
from Pmv.pmvPalettes import Shapely
from Pmv.pmvPalettes import SecondaryStructureType

class ePMVsynchro:
    
    def __init__(self,epmv,period=0.1):
        self.period = period
        self.callback = None
        self.epmv = epmv
        self.mv = self.epmv.mv
        self.timeControl = oma.MAnimControl()

    def change_period(self,newP):
        self.period = newP
        self.remove_callback()
        self.set_callback()
        
    def set_callback(self):
        self.callback = OpenMaya.MTimerMessage.addTimerCallback(self.period,self.doit)

    def remove_callback(self):
        OpenMaya.MMessage.removeCallback(self.callback)
        
    def doit(self,period,time,userData=None):
        #need to get the current selection
        # Create a selection list iterator
        #
#        print "playing", self.timeControl.isPlaying()
#        sIter = OpenMaya.MItSelectionList(slist)
        if self.epmv.synchro_timeline and self.timeControl.isPlaying(): #should I check isPlaying ?
            traj = self.epmv.gui.current_traj
#            #getCurrent time
            t = self.timeControl.currentTime()
            frame = int(t.asUnits(OpenMaya.MTime.kFilm))
#            frame=doc.GetTime().GetFrame(fps)
            st,ft=self.epmv.synchro_ratio
            if (frame % ft) == 0:   
                step = frame * st
                self.epmv.updateData(traj,step)
        else :
            slist = OpenMaya.MSelectionList()
            if not slist : 
               return 
            OpenMaya.MGlobal.getActiveSelectionList(slist)
            selection = []
            slist.getSelectionStrings(selection)
            self.epmv.updateCoordFromObj(selection,debug=True)
        self.epmv.helper.update()

class mayaAdaptor(epmvAdaptor):
    
    def __init__(self,gui=False,mv=None,debug=0):
        self.soft = 'maya'
        self.helper = helperMaya.mayaHelper()
        epmvAdaptor.__init__(self,mv,host='maya',debug=debug)
        #scene and object helper function
#        self._getCurrentScene = mayaHelper.getCurrentScene
        self._getCurrentScene = self.helper.getCurrentScene
##        self._addObjToGeom = self.helper.addObjToGeom
#        self._host_update = self.helper.update
##        self._parseObjectName = self.helper.parseObjectName
        self._getObjectName = self.helper.getName
        self._getObject = self.helper.getObject
        self._addObjectToScene = self.helper.addObjectToScene
        self._toggleDisplay = self.helper.toggleDisplay
        self._newEmpty = self.helper.newEmpty
        self._metaballs = self.helper.metaballs
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
#        self.use_progressBar = False
#        if not hasattr(maya,'pb') : 
#            maya.pb = None    
        #define the general function
        self.use_progressBar = False
        self._resetProgressBar = self.helper.resetProgressBar
        self._progressBar = self.helper.progressBar
        self.rep = "epmv"
        #specific options
        self.keywords["spherestype"]={"name":"use nurbs sphere instead of polygonal one","value":True,"type":"checkbox"}

    def synchronize(self):
        if self.synchro_realtime:
            if not hasattr(self,"epmv_synchro") or self.epmv_synchro is None:
                self.epmv_synchro = ePMVsynchro(self,period=0.1)
            self.epmv_synchro.set_callback()
        else :
            if hasattr(self,"epmv_synchro") and self.epmv_synchro is not None :
                self.epmv_synchro.remove_callback()
#                self.epmv_synchro = None
        
    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self._getCurrentScene()
        if shape is None :
            # create full circle at origin on the x-y plane
            obj,circle = maya.cmds.circle(n="Circle", nr=(1, 0, 0), c=(0, 0, 0),r=0.3 ) 
            #return obj (Circle) and makenurbeCircle but not the CircleShape
            shape = "CircleShape"
        if spline is None :
            obSpline,spline,extruded = self.helper.spline(name,coords,
                                                    extrude_obj=shape,scene=sc,
                                                    parent =parent)
        #if parent is not None :
        #    parent.makeParent([obSpline])
        return obSpline#,extruded

    def _createBaseSphere(self,name="",quality=0,radius=None,cpkRad=0.0,
                         scale=1.0,scene=None,parent=None):
        if self.spherestype :
            typeSp = "nurb"
        else :
            typeSp = "poly"
        iMe={}
        baseparent=self.helper.getObject(name,doit=True)
        #quality =>res
        if baseparent is None:    
            baseparent=self.helper.newEmpty(name)
            self.helper.addObjectToScene(self.helper.getCurrentScene(),
                                         baseparent,parent=parent)
            self.helper.toggleDisplay(baseparent,False)
        for atn in  self.AtmRadi.keys():
#            atparent=self.helper.getObject(name+"_"+atn,doit=True)
            rad=float(self.AtmRadi[atn])
#            if atparent is None :
#                atparent=self.helper.newEmpty(name+"_"+atn)
#                self.helper.addObjectToScene(self.helper.getCurrentScene(),
#                                             atparent,parent=baseparent)
            iMe[atn]=self.helper.getObject(name+'_'+atn,doit=True)
            if not iMe[atn]:
                pobj,iMe[atn]=self.helper.Sphere(name+'_'+atn,mat = atn,type=typeSp)
#                iMe[atn],node=cmds.sphere(name=name+"Atom_"+atn,r=rad)#float(scaleFactor) ) #nurbsphere
                self.helper.addObjectToScene(self.helper.getCurrentScene(),
                                             iMe[atn],parent=baseparent)
                #iMe[atn]=atparent
#                self.assignMaterial(atn, iMe[atn])
                #cmds.sets (nodeName, e=True, fe='initialShadingGroup')
    #        toggleDisplay(iMe[atn],False)
        return iMe


    def _instancesAtomsSphere(self,name,x,iMe,scn,mat=None, scale=1.0,Res=32,R=None,
                             join=0,geom=None,pb=False):
        sphers=[]
        k=0
        n='S'
        nn = 'cpk'
        if scale == 0.0 : scale = 1.0    
        #if mat == None : mat=create_Atoms_materials()    
        if name.find('balls') != (-1) : 
            n='B'
            nn='balls'
        #print name
        if geom is not None:
            coords=geom.getVertices()
        else :
            coords=x.coords
        #import maya
        pb = self.use_progressBar    
        hiera = 'default'        
        mol = x[0].getParentOfType(Protein)        
        #parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])  
        parent=self.findatmParentHierarchie(x[0],n,hiera)
        if pb :
            self.helper.resetProgressBar()
        for c in mol.chains:
            if pb :
                self.helper.progressBar(label="chain :"+c.name)
            spher=[]
            oneparent = True 
            atoms = c.residues.atoms
#            if pb != None  : 
#                maya.cmds.progressBar(maya.pb, edit=True, maxValue=len(atoms.coords),progress=0)
            parent=self.findatmParentHierarchie(atoms[0],n,hiera) 
            hierarchy=atoms[0].full_name().split(":")   
            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_"+nn])
            def oneinstance(at,pb=False):
                atN=at.name
                if atN[0] not in self.AtmRadi.keys(): atN="A"
                fullname = self.atomNameRule(at,n)
                atC=at.coords
                sph = self.helper.newMInstance(fullname,iMe[atN[0]],location=atC,parent = parent)
                #self.helper.addObjectToScene(self.helper.getCurrentScene(),sph,parent=parent)
                self.helper.toggleDisplay(sph,False)
                if pb :
                    self.helper.progressBar(progress = 1)
                return sph
            spher = [oneinstance(at,pb=pb) for at in atoms]   
            sphers.extend(spher)
        if pb :
            self.helper.resetProgressBar()
        return spher

    def _changeColor(self,geom,colors,perVertex=True,perObjectmat=None,pb=False):
        if hasattr(geom,'mesh'):
            objToColor = geom.mesh
        else :
            if type(geom) is str :
                objToColor = self.helper.getObject(geom)
            else :
                objToColor = geom        
        self.helper.changeColor(objToColor,colors,perVertex=perVertex,
                         perObjectmat=perObjectmat,pb=pb)

    def _armature(self,name, atomset,coords=None,scn=None,root=None):
        if coords is not None :
            c = coords
        else :
            c = atomset.coords
        object,bones=self.helper.armature(name, c,scn=scn,root=root)
        return object,bones

#    def atomNameRule(self,atom,prefix):
#        return prefix+"_"+atom.full_name().replace(":","_").replace(" ","_").replace("'","b")+"n"+str(atom.number)
#
#    def splitName(self,name):
#    #general function-> in the adaptor ?
#        #T_3bna_A_C11_P_OP2
#        #"T_"+molname+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
#        if name[0] == "T" : #sticks name.. which is "T_"+chname+"_"+Resname+"_"+atomname+"_"+atm2.name\n'
#            tmp=name.split("_")
#            return ["T",tmp[1],tmp[2],tmp[3][0:1],tmp[3][1:],tmp[4]]
#        else :
#            #case where 2 __ S_3bna_A__DC3_O2 A. This depend also on the atomNameRule
#            tmp=name.split("_")
#            indice=tmp[0]#.split("_")[0]
#            molname=tmp[1]#.split("_")[1]
#            chainname=tmp[2]
#            ires = 3
#            if len(tmp) > 5 :
#                ires = 4
#            residuename=tmp[ires][0:3]
#            residuenumber=tmp[ires][3:]
#            atomname=tmp[ires+1]
#            return [indice,molname,chainname,residuename,residuenumber,atomname]

    def updateMolAtomCoordBones(self,mol,index=-1):
        #problem, theses are only CA
        vt = []
        bones = mol.geomContainer.geoms["armature"][1]
        vt = [self.helper.ToVec(self.helper.getJointPosition(j)) for j in bones]
        print len(vt),vt[0]
        return vt
    
    def updateMolAtomCoordSpline(self,mol,index=-1):
        #problem, theses are only CA
        vt = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        name=mol.name+"_"+mol.chains[0].name+"spline"
        #get the point from the curve
        points=self.helper.getSplinePoints(name+"Shape")
#        spline = self.helper.getCurrentScene().SearchObject(name)
#        points = spline.GetAllPoints()
    #    matr= mesh.GetMg()
        vt = [self.helper.ToVec(points[x]) for x in range(points.length())]
        return vt
        
    def updateMolAtomCoordLines(self,mol,index=-1):
        pass
        #no lines in maya ? -> particles ?
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        vt = []
#        mesh = mol.geomContainer.geoms[mol.chains[0].full_name()+'_line'][0]
#        points = mesh.GetAllPoints()
#        matr= mesh.GetMg()
#        vt=[self.helper.vc4d(x*matr) for x in points]
#        #these are the cpk
#        if hasattr(mol.geomContainer.geoms['cpk'],'obj'):
#            sph = mol.geomContainer.geoms['cpk'].obj
#            #each have to be translate
#            [x.SetAbsPos(p) for x,p in zip(sph,points)]
#            #map(lambda x,p:x.SetAbsPos(p),sph,points)
#            masterCPK=sph[0].GetUp()
#            masterCPK.SetMg(matr)
        return vt#updateMolAtomCoordCPK(mol,index=index)
        
        
    def createGUI(self):
        self.gui = epmvGui(epmv=self,rep='epmv')

