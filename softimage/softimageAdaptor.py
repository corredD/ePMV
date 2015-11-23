
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/softimage/softimageAdaptor.py is part of ePMV.

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
import sys
import os
from ePMV import epmvAdaptor
#from ePMV.epmvAdaptor import epmvAdaptor
from upy.softimage.v2013 import softimageHelper

from ePMV.lightGridCommands import addGridCommand
from ePMV.lightGridCommands import readAnyGrid
from ePMV.lightGridCommands import IsocontourCommand

from Pmv.mvCommand import MVCommand
from Pmv.moleculeViewer import MoleculeViewer
from Pmv.moleculeViewer import DeleteGeomsEvent, AddGeomsEvent, EditGeomsEvent
from Pmv.moleculeViewer import DeleteAtomsEvent, EditAtomsEvent
from Pmv.deleteCommands import BeforeDeleteMoleculesEvent,AfterDeleteAtomsEvent
from Pmv.displayCommands import BindGeomToMolecularFragment
from Pmv.trajectoryCommands import PlayTrajectoryCommand

from mglutil.util.recentFiles import RecentFiles

from MolKit.protein import Protein
from Pmv.pmvPalettes import AtomElements
#from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
#from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
#from Pmv.pmvPalettes import Shapely
#from Pmv.pmvPalettes import SecondaryStructureType

class softimageAdaptor(epmvAdaptor.epmvAdaptor):
    """
    The specific adaptor for 3dsMax.
    
    epmv = maxAdaptor(debug=1)
    epmv.mv.readMolecule("/Users/ludo/blenderKTF/1CRN.pdb")
    epmv.mv.computeMSMS("1CRN")
    epmv.mv.computeMSMS("1CRN", log=1, display=True, perMol=1,surfName="MSMS-MOL1CRN")
    epmv.mv.displayCPK("1CRN",log=1,negate=False,scaleFactor = 1.0)
    ...
    """

    def __init__(self,gui=False,mv=None,debug=0):
        self.host = "softimage"
        self.helper = softimageHelper.softimageHelper()
        epmvAdaptor.epmvAdaptor.__init__(self,mv,host='softimage',debug=debug)
        self.MAX_LENGTH_NAME = 30
        self.useLog = False
        self.duplicatemol = False
        self.soft = 'softimage'
        #scene and object helper function
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
        self._PointCloudObject = self.helper.PointCloudObject
#        #modify/update geom helper function
##        self._updateSphereMesh = self.helper.updateSphereMesh
        self._updateSphereObj = self.helper.updateSphereObj
#        self._updateSphereObjs = self.helper.updateSphereObjs
#        self._updateTubeMesh = self.helper.updateTubeMesh
 #       self._updateTubeObj = self.helper.updateTubeObj
#        self._updateMesh = self.helper.updateMesh
#        #color helper function
#        self._changeColor = self.helper.changeColor
#        self._checkChangeMaterial = self.helper.checkChangeMaterial
#        self._changeSticksColor = self.helper.changeSticksColor
#        self._checkChangeStickMaterial = self.helper.checkChangeStickMaterial
        #define the general function
        self.use_progressBar = False
        self.colorProxyObject = True
        self._progressBar = self.helper.progressBar
        self._resetProgressBar = self.helper.resetProgressBar
#        self._render = self.helper.render
        self.rep = "MaxPlus"#self._getCurrentScene().GetDocumentName()
#    def _progressBar(self,progress,label):
#        #the progessbar use the StatusSetBar
#        c4d.StatusSetText(label)
#        c4d.StatusSetBar(int(progress*100.))
#
#    def _resetProgressBar(self,value):
#        c4d.StatusClear()


    def setupMV(self):
        self.mv.browseCommands('fileCommands', package="Pmv", topCommand=0)
        self.mv.browseCommands('bondsCommands',package='Pmv', topCommand=0)
        self.mv.browseCommands('deleteCommands',package='Pmv', topCommand=0)
        self.mv.browseCommands('displayCommands',
                    commands=['displaySticksAndBalls','undisplaySticksAndBalls',
                              'displayCPK', 'undisplayCPK',
                              'displayLines','undisplayLines',
                              'displayBackboneTrace','undisplayBackboneTrace',
                              'DisplayBoundGeom'], package='Pmv', topCommand=0)
        self.mv.browseCommands('editCommands',package='Pmv', topCommand=0)
        self.mv.browseCommands("secondaryStructureCommands", package="Pmv", topCommand=0)
        self.mv.browseCommands('beadedRibbonsCommands', package="ePMV", topCommand=0)
        self.mv.browseCommands("splineCommands", package="Pmv", topCommand=0)
        self.mv.browseCommands("coarseMolSurfaceCommands", package="Pmv", topCommand=0)
        self.mv.browseCommands('msmsCommands',
                               commands=['computeMSMS','displayMSMS', 'undisplayMSMS',
                                         'readMSMS', 'saveMSMS', 'computeSESAndSASArea',],
                               package='Pmv', topCommand=0)
        self.mv.browseCommands('selectionCommands', commands=['select', 'deselect',
                                                   'clearSelection', 'saveSet',
                                                   'invertSelection',
                                                   'selectSet',
                                                   'selectFromString',
                                                   'directSelect','selectHeteroAtoms'],
                                package='Pmv', topCommand=0)
        self.mv.browseCommands('APBSCommands_2x', package='ePMV.pmv_dev', topCommand=0)
        self.mv.browseCommands('colorCommands',package='ePMV.pmv_dev', topCommand=0)        
        self.mv.browseCommands('buildDNACommands',package='ePMV.pmv_dev', topCommand=0)#commands=['buildDNA']
        self.mv.browseCommands('repairCommands', package='Pmv', topCommand=0)
        self.mv.browseCommands("dejaVuCommands", package="ViewerFramework", topCommand=0)
        self.mv.browseCommands('displayCommands',
                    commands=['showMolecules'],
                    package='Pmv', topCommand=0)
        self.mv.browseCommands('helpCommands',package ='Pmv', topCommand =0)

        self.mv.browseCommands('superimposeCommandsNew', package='Pmv', topCommand=0)
        self.mv.browseCommands('setangleCommands', package='Pmv', topCommand=0)
        self.mv.setUserPreference(('Transformation Logging', 'final'), topCommand=0)
        self.mv.setUserPreference(('Show Progress Bar', 'show'), topCommand=0)
        self.mv.setUserPreference(('Sharp Color Boundaries for MSMS', 'blur'), topCommand=0)
        self.mv.browseCommands('serverCommands', commands=[
                    'startServer', 'connectToServer', 'StartWebControlServer'],
                    package='ViewerFramework', topCommand=0)
        self.mv.addCommand(BindGeomToMolecularFragment(), 'bindGeomToMolecularFragment', None)
        self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        self.mv.addCommand(PlayTrajectoryCommand(),'playTrajectory',None)
        self.mv.addCommand(addGridCommand(),'addGrid',None)
        self.mv.addCommand(readAnyGrid(),'readAny',None)
        self.mv.addCommand(IsocontourCommand(),'isoC',None)
        #define the listener
        if self.host is not None :
            self.mv.registerListener(DeleteGeomsEvent, self.updateGeom)
            self.mv.registerListener(AddGeomsEvent, self.updateGeom)
            self.mv.registerListener(EditGeomsEvent, self.updateGeom)
            self.mv.registerListener(AfterDeleteAtomsEvent, self.updateModel)
            self.mv.registerListener(BeforeDeleteMoleculesEvent,self.updateModel)
            self.mv.addCommand(epmvAdaptor.loadMoleculeInHost(self),'_loadMol',None)            
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
        rcFile = self.mv.rcFolder
        if rcFile:
            rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
            self.mv.recentFiles = RecentFiles(self.mv, None, filePath=rcFile,index=0)
        else :
            print("no rcFolder??")
        
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
#        mv.hostApp.driver.bicyl = self.bicyl
        

    def synchronize(self):
        pass

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
##        sc=self._getCurrentScene()
##        if shape is None :
##            circle=self.helper.Circle(name+"circle",rad=0.5)
##            self._addObjectToScene(sc,circle)
##        if spline is None :
##            spline = self.helper.spline(name+"_spline",coords,scene=sc)
###            self._addObjectToScene(sc,spline[0])
##        nurb=self.helper.sweepnurbs(name)
##        self._addObjectToScene(sc,nurb,parent=parent)
##        self.helper.reParent(spline[0],nurb)
##        self.helper.reParent(circle,nurb)
        return None
    #name=str(mol.name+"_b_cpk"),quality=opts[4],cpkRad=opts[3],
    #                                    scale=opts[2],parent=root
    def _createBaseSphere(self,name="",quality=0,cpkRad=0.,scale=1.,radius=1.,
                         parent=None,**kw):
        #print ("name "+name+"XX")
        QualitySph={"0":15,"1":3,"2":6,"3":8,"4":16,"5":32} 
        segments = QualitySph[str(quality)]
        iMe={}
        doc = self.helper.getCurrentScene()
        baseparent=self.helper.getObject(name)
        #print ("get "+str(baseparent is None))
        if baseparent is None :
            baseparent=self.helper.newEmpty(name,parent=parent)
            #print baseparent,(baseparent is None)
            #self.helper.addObjectToScene(doc,baseparent,parent=parent)
            #self.helper.toggleDisplay(baseparent,False)
        baseShape = self.helper.getObject(name+"_shape")
        if baseShape is None :
            baseShape = self.helper.newEmpty(name+"_shape")
            self.helper.addObjectToScene(doc,baseShape,parent=baseparent)
        basesphere=self.helper.getObject(name+"basesphere")
        if basesphere is None : 
            meshsphere,basesphere=self.helper.Sphere(name+"basesphere",res=segments,
                                                     parent=baseShape)
#            self.helper.toggleDisplay(basesphere,display=False)
        for atn in list(self.AtmRadi.keys()):
            #when we create we dont want to scale, just take the radius
            rad=float(self.AtmRadi[atn])
            atparent=self.helper.getObject(name+"_"+atn)
            if atparent is None :
                atparent=self.helper.newEmpty(name+"_"+atn,parent=baseparent)
            iMe[atn]= self.helper.getMesh("mesh_"+name+'_'+atn)
            if iMe[atn] is None :
#                iMe[atn],ob=self.helper.Sphere(name+'_'+atn,
#                                                     res=segments,
#                                                     mat = atn)
                iMe[atn],basesphere=self.helper.Sphere("mesh_"+atn+"_"+name,res=segments,
                                                     parent=atparent,radius=float(rad))
                #iMe[atn] = self.helper.newInstance("mesh_"+atn+"_"+name,meshsphere)#baseSphere
                #self.helper.scaleObj(iMe[atn],float(rad))
                #iMe[atn]=c4d.BaseObject(c4d.Osphere)
                #self.helper.addObjectToScene(doc,atparent,parent=baseparent)
                #self.helper.addObjectToScene(doc,iMe[atn],parent=atparent)
                iMe[atn]=atparent
        self.helper.toggleDisplay(baseparent,False)#this dhould toggle everything   
        return iMe

    def _changeColor(self,geom,colors,perVertex=True,proxyObject=True,pb=False):
        if hasattr(geom,'mesh'):
            if geom.name[:4] in ['Heli', 'Shee', 'Coil', 'Turn', 'Stra']:
                proxyObject=False       
            objToColor = geom.obj
        elif hasattr(geom,"obj"):
            objToColor = geom.obj
        else :
            objToColor = None            
        if hasattr(geom,"name") :
            if geom.name[:4] in ['secondarystructure','Heli', 'Shee', 'Coil', 'Turn', 'Stra']:
                proxyObject=False
        if objToColor is None :
            if type(geom) is str :
                objToColor = self.helper.getObject(geom)
            elif type(geom) is list :
                objToColor = geom[0]
                if type(geom) is str :
                    objToColor = self.helper.getObject(geom)
                else :
                    objToColor = geom
            else :
                objToColor = geom
        self.helper.changeColor(objToColor,colors,perVertex=perVertex,pb=pb,proxyObject=False )

    def _armature(self,name,atomset,coords=None,root=None,scn=None):
        scn=self.helper.getCurrentScene()
        names = None
        if coords is not None :
            c = coords    
        else :
            c = atomset.coords
            names = [x.full_name().replace(":","_") for x in atomset]
        #object,bones=self.helper.armature(name,c,listeName=names,
        #                                  root=root,scn=scn)
        return None,None#object,bones

    def _metaballs(self,name,coords,radius,scn=None,root=None):
        #by default we build the clouds metaballs...maybe could do on particle
        basename = name.split("_")[0] #basename form : mol.name+"_metaball"
        cloud = self.helper.getObject(name+"_cloud")
        if cloud is None :
            cloud = self.helper.PointCloudObject(name+"_cloud",
                                        vertices=coords,
                                        parent=None,atomarray=False)[0]
        #metab=self.helper.create_metaballs(name,sourceObj=cloud,parent=root,
        #                                   coords=coords)
        return [None,None]
        
    def createGUI(self):
        self.gui = epmvGui(epmv=self,rep=self.rep)
        
    def updateSphereObjs(self,g):
        if not hasattr(g,'obj') : return
        newcoords=g.getVertices()
        #print "upadteObjSpheres"
        #[self.helper.updateObjectPos(g.obj[i],newcoords[i]) for i in range(len(g.obj))]       
    
    def updateMolAtomCoordBones(self,mol,index=-1):
        #problem, theses are only CA
        vt = []
        bones = mol.geomContainer.geoms["armature"][1]
        #vt = [self.helper.ToVec(j.GetMg().off) for j in bones]
#        for join in bones:
#            pos=join.GetMg().off
#            vt.append(self.helper.ToVec(pos))
        #print(vt[0])
        return vt
    
    def updateMolAtomCoordSpline(self,mol,index=-1):
        #problem, theses are only CA
        vts = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        #for ch in mol.chains:
        #    name=mol.name+"_"+ch.name+"spline"
        #    @spline = self.helper.getCurrentScene().SearchObject(name)
        #    points = spline.GetAllPoints()
        #    matr= spline.GetMg()
        #    vt=[self.helper.ToVec(x*matr) for x in points]
            #vt = map(lambda x,m=matr: ToVec(x),points)
            #vt = [self.helper.ToVec(x) for x in points]
         #   vts.append(vt)
        return vts
        
    def updateMolAtomCoordLines(self,mol,index=-1):
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        vts = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        for ch in mol.chains:
            vt=[]
            mesh = mol.geomContainer.geoms[ch.full_name()+'_line'][0]
            #check the derform mode before
            #deform = mesh.GetDeformMode()
            #meshcache = mesh.GetDeformCache()
            #if meshcache is not None:
            #    meshcache = mesh.GetDeformCache()
            #    points = meshcache.GetAllPoints()
            #    vt=[self.helper.ToVec(x) for x in points]
           # else :
            #    points = mesh.GetAllPoints()
            #    matr= mesh.GetMg()
            #    vt=[self.helper.ToVec(x*matr) for x in points]
            #vts.extend(vt)
        #vt = map(lambda x,m=matr: ToVec(x*m),points)
        #these are the cpk
        #if hasattr(mol.geomContainer.geoms['cpk'],'obj'):
            #sph = mol.geomContainer.geoms['cpk'].obj
            #each have to be translate
            #[x.SetAbsPos(self.helper.FromVec(p)) for x,p in zip(sph,vts)]
            #map(lambda x,p:x.SetAbsPos(p),sph,points)
           # masterCPK=sph[0].GetUp()
            #if meshcache is None:
            #    masterCPK.SetMg(matr)
        return vts#updateMolAtomCoordCPK(mol,index=index)
        

#    def display_CPK(self,mol,sel,display,needRedraw=False,quality=0,cpkRad=0.0,scaleFactor=1.0,useTree="default",dialog=None):
#        sc = self.getCurrentScene()
#        g = mol.geomContainer.geoms['cpk']
#        #print g
#        #name=selection+"_cpk"
#        #select=self.select(selection,negate=False, only=True, xor=False, log=0, 
#        #                   intersect=False)
#        #print name,select
#        #sel=select.findType(Atom)
#        if not hasattr(g,"obj"): #if no mesh have to create it for evey atms
#            name=mol.name+"_cpk"
#            #print name
#            mesh=createBaseSphere(name="base_cpk",quality=quality,cpkRad=cpkRad,
#                                  scale=scaleFactor,parent=mol.geomContainer.masterGeom.obj)
#            ob=instancesAtomsSphere(name,mol.allAtoms,mesh,sc,scale=scaleFactor,
#                                    Res=quality,join=0,dialog=dialog)
#            addObjToGeom([ob,mesh],g)
#            for i,o in enumerate(ob):
#    #            if dialog != None :
#    #                dialog.bc[c4d.gui.BFM_STATUSBAR_PROGRESS] = j/len(coords)
#    #                #dialog.bc[c4d.gui.BFM_STATUSBAR_PROGRESSFULLSIZE] = True
#    #                dialog.set(dialog._progess,float(i/len(ob)))#dialog.bc)
#    #                getCurrentScene().Message(c4d.MULTIMSG_UP)       
#    #                c4d.draw_views(c4d.DA_ONLY_ACTIVE_VIEW|c4d.DA_NO_THREAD|c4d.DA_NO_ANIMATION)
#                parent=mol.geomContainer.masterGeom.obj
#                hierarchy=parseObjectName(o)
#                if hierarchy != "" :
#                    if useTree == 'perRes' :
#                        parent = getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
#                    elif useTree == 'perAtom' :
#                        parent = getObject(o.GetName().split("_")[1])
#                    else :
#                        parent = getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_cpk"])                
#                addObjectToScene(sc,o,parent=parent)
#                toggleDisplay(o,False) #True per default
#                
#        #elif hasattr(g,"obj")  and display : 
#            #updateSphereMesh(g,quality=quality,cpkRad=cpkRad,scale=scaleFactor) 
#            #if needRedraw : updateSphereObj(g)
#        #if hasattr(g,"obj"):
#        else :
#            updateSphereMesh(g,quality=quality,cpkRad=cpkRad,scale=scaleFactor)
#            atoms=sel#findType(Atom) already done
#            for atms in atoms:
#                nameo = "S_"+atms.full_name()
#                o=getObject(nameo)#Blender.Object.Get (nameo)
#                if o != None :
#                    toggleDisplay(o,display)
#                    if needRedraw : updateObjectPos(o,atms.coords) 

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
    
                    lines = self.helper.createsNmesh(ch.full_name()+'_line',
                                                     ch.residues.atoms.coords,
                                                     None,indices)
                    #self.helper.addObjectToScene(scn,lines[0],parent=arr)
                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
                    #display using AtomArray
                else : #need to update
#                    self.helper._updateLines(lines, chains=ch)
                    self.helper.updatePoly(lines,vertices=ch.residues.atoms.coords)
                    
    def _addObjToGeom(self,obj,geom):
        if type(obj) == list or type(obj) == tuple:
            if len(obj) > 2: geom.obj=obj
            elif len(obj) == 1: 
                geom.obj=self.helper.getName(obj[0])
                geom.mesh=self.helper.getName(obj[0])
            elif len(obj) == 2:
                if type(obj[0]) == list or type(obj[0]) == tuple:    
                    geom.obj=[]
                    if type(obj[1]) == list or type(obj[1]) == tuple: 
                        geom.mesh=obj[1][:]
                    elif type(obj[1]) == dict :
                        geom.mesh={}                                                
                        for me in list(obj[1].keys()):
                            #name of the node
                            geom.mesh[me]=self.helper.getName(obj[1][me])#should be the sphere?
                    else :
                        geom.mesh=obj[0]#1-probalm with 3dsMax, name of Mesh is 'Mesh'#self.helper.getName(
                    geom.obj= obj[0][:]
                else :
                    geom.mesh=obj[1]
                    geom.obj=self.helper.getName(obj[0])
        else : geom.obj=self.helper.getName(obj)    