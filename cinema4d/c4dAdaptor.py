#############################################################################
#
# Author: Ludovic Autin
#
# Copyright: Ludovic Autin TSRI 2010
#
#
#############################################################################

from ePMV.epmvAdaptor import epmvAdaptor
from pyubic.cinema4d import helperC4D

import c4d
from c4d import gui

from MolKit.protein import Protein
from Pmv.pmvPalettes import AtomElements
#from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
#from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
#from Pmv.pmvPalettes import Shapely
#from Pmv.pmvPalettes import SecondaryStructureType

class c4dAdaptor(epmvAdaptor):
    """
    The specific adaptor for C4D R12.
    
    from Pmv.hostappInterface.cinema4d_dev.c4dAdaptor import c4dAdaptor
    epmv = c4dAdaptor(debug=1)
    epmv.mv.readMolecule("/Users/ludo/blenderKTF/1CRN.pdb")
    epmv.mv.computeMSMS("1CRN")
    epmv.mv.computeMSMS("1CRN", log=1, display=True, perMol=1,surfName="MSMS-MOL1CRN")
    epmv.mv.displayCPK("1CRN",log=1,negate=False,scaleFactor = 1.0)
    ...
    """

    def __init__(self,gui=False,mv=None,debug=0):
        epmvAdaptor.__init__(self,mv,host='c4d',debug=debug)
        self.soft = 'c4d'
        self.helper = helperC4D.c4dHelper()
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
        self.use_progressBar = False
        self.colorProxyObject = True
        self._progressBar = self.helper.progressBar
        self._resetProgressBar = self.helper.resetProgressBar
#        self._render = self.helper.render
        self.rep = self._getCurrentScene().GetDocumentName()
#    def _progressBar(self,progress,label):
#        #the progessbar use the StatusSetBar
#        c4d.StatusSetText(label)
#        c4d.StatusSetBar(int(progress*100.))
#
#    def _resetProgressBar(self,value):
#        c4d.StatusClear()

    def synchronize(self):
        root = self.helper.getObject("ePMV")
        if self.synchro_realtime and root is None :
            root = self.helper.newEmpty("ePMV")
            root.MakeTag(102374500)
            self.helper.addObjectToScene(self.helper.getCurrentScene(),root)

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self._getCurrentScene()
        if shape is None :
            circle=self.helper.Circle(name+"circle",rad=0.3)
            self._addObjectToScene(sc,circle)
        if spline is None :
            spline = self.helper.spline(name+"spline",coords,scene=sc)
#            self._addObjectToScene(sc,spline[0])
        nurb=self.helper.sweepnurbs(name)
        self._addObjectToScene(sc,nurb,parent=parent)
        self.helper.reParent(spline[0],nurb)
        self.helper.reParent(circle,nurb)
        return nurb

    def _createBaseSphere(self,name="",quality=0,cpkRad=0.,scale=1.,radius=1.,
                         parent=None,scene=None):
#        name=mol.name+"_b_cpk",quality=opts[4],cpkRad=opts[3],
#                                        scale=opts[2],parent=root
        QualitySph={"0":15,"1":3,"2":6,"3":8,"4":16,"5":32} 
        segments = QualitySph[str(quality)]
        iMe={}
        doc = self.helper.getCurrentScene()
        baseparent=self.helper.getObject(name)
        if baseparent is None :
            baseparent=self.helper.newEmpty(name)
            self.helper.addObjectToScene(doc,baseparent,parent=parent)
            self.helper.toggleDisplay(baseparent,False)
        baseShape = self.helper.getObject(name+"_shape")
        if baseShape is None :
            baseShape = self.helper.newEmpty(name+"_shape")
            self.helper.addObjectToScene(doc,baseShape,parent=baseparent)
        basesphere=self.helper.getObject(name+"basesphere")
        if basesphere is None : 
            meshsphere,basesphere=self.helper.Sphere(name+"basesphere",res=segments,
                                                     parent=baseShape)
#            self.helper.toggleDisplay(basesphere,display=False)
        for atn in self.AtmRadi.keys():
            #when we create we dont want to scale, just take the radius
            rad=float(self.AtmRadi[atn])
            atparent=self.helper.getObject(name+"_"+atn)
            if atparent is None :
                atparent=self.helper.newEmpty(name+"_"+atn)
            iMe[atn]= self.helper.getMesh("mesh_"+name+'_'+atn)
            if iMe[atn] is None :
#                iMe[atn],ob=self.helper.Sphere(name+'_'+atn,
#                                                     res=segments,
#                                                     mat = atn)
                iMe[atn] = self.helper.setInstance("mesh_"+atn+"_"+name,baseShape)
                self.helper.scaleObj(iMe[atn],float(rad))
                #iMe[atn]=c4d.BaseObject(c4d.Osphere)
                self.helper.addObjectToScene(doc,atparent,parent=baseparent)
                self.helper.addObjectToScene(doc,iMe[atn],parent=atparent)
                iMe[atn]=atparent   
        return iMe

    def _changeColor(self,geom,colors,perVertex=True,proxyObject=True,pb=False):
        if geom.name[:4] in ['Heli', 'Shee', 'Coil', 'Turn', 'Stra']:
            proxyObject=False
        self.helper.changeColor(geom.mesh,colors,perVertex=perVertex,
                                    proxyObject=proxyObject,pb=pb)

    def _armature(self,name,atomset,root=None,scn=None):
        names = [x.full_name().replace(":","_") for x in atomset]
        scn=self.helper.getCurrentScene()
        object,bones=self.helper.armature(name,atomset.coords,listeName=names,
                                          root=root,scn=scn)
        return object,bones

    def _metaballs(self,name,coords,radius,scn=None,root=None):
        #by default we build the clouds metaballs...maybe could do on particle
        basename = name.split("_")[0] #basename form : mol.name+"_metaball"
        cloud = self.helper.getObject(name+"_cloud")
        if cloud is None :
            cloud = self.helper.PointCloudObject(name+"_cloud",
                                        vertices=coords,
                                        parent=None,atomarray=False)
        metab=self.helper.create_metaballs(name,sourceObj=cloud,parent=root,
                                           coords=coords)
        return [None,metab]
        
    def _instancesAtomsSphere(self,name,x,iMe,scn,mat=None,scale=1.0,Res=32,
                            R=None,join=0,geom=None,dialog=None,pb=False):
        #radius made via baseMesh...
        #except for balls, need to scale?#by default : 0.3? 
        if scn == None :
            scn=self.helper.getCurrentScene()
        sphers=[]
        k=0
        n='S'
        if name.find('balls') != (-1) : n='B'
        
        if geom is not None:
            coords=geom.getVertices()
        else :
            coords=x.coords
        hiera = 'default'    
        parent=self.findatmParentHierarchie(x[0],n,hiera) 
        mol = x[0].getParentOfType(Protein)        
        for c in mol.chains:
            spher=[]
            oneparent = True 
            atoms = c.residues.atoms
            parent=self.findatmParentHierarchie(atoms[0],n,hiera)
            #print "finded",parent        
            for j in xrange(len(atoms.coords)):
                #at=res.atoms[j]
                at=atoms[j]
                radius = at.radius
#                scaleFactor=float(R)+float(radius)*float(scale)
                atN=at.name
                if atN[0] not in AtomElements.keys() : atN="A"
                fullname = at.full_name()
                #print fullname
                atC=at.coords#at._coords[0]
                spher.append( c4d.BaseObject(c4d.Oinstance) )
                spher[j][1001]=iMe[atN[0]]
                #spher[j][1001]=1        
                spher[j].SetName(n+"_"+fullname)#.replace(":","_")
                sc = iMe[atN[0]][905].x #radius of parent mesh
                #if sc != scaleFactor : 
#                if n=='B' :
#                    scale = 1.
#                    spher[j][905]=c4d.Vector(float((1/sc)*scale),float((1/sc)*scale),float((1/sc)*scale))                #
                spher[j].SetAbsPos(self.helper.c4dv(atC))
                texture = spher[j].MakeTag(c4d.Ttexture)
                texture[1010] = self.helper.getMaterial(atN[0])
                p = self.findatmParentHierarchie(at,n,hiera)
                #print "dinded",p
                if parent != p : 
                    cp = p
                    oneparent = False
                    parent = p
                else :
                    cp = parent                            
                #print "parent",cp
                self.helper.addObjectToScene(self.helper.getCurrentScene(),spher[j],parent=cp)
                self.helper.toggleDisplay(spher[j],False)
                k=k+1
                if pb :
                    self.helper.progressBar(j/len(coords)," cpk ")
                    #dialog.bc[c4d.gui.BFM_STATUSBAR_PROGRESS] = j/len(coords)
                    #dialog.bc[c4d.gui.BFM_STATUSBAR_PROGRESSFULLSIZE] = True
                    #c4d.StatusSetBar(j/len(coords))
                    self.helper.update()
            sphers.extend(spher)
        if pb :
            self.helper.resetProgressBar(0)
        return sphers
        
    def createGUI(self):
        self.gui = epmvGui(epmv=self,rep=self.rep)
        
    def updateSphereObjs(self,g):
        if not hasattr(g,'obj') : return
        newcoords=g.getVertices()
        #print "upadteObjSpheres"
        [self.helper.updateObjectPos(g.obj[i],newcoords[i]) for i in range(len(g.obj))]       
    
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
        vt = [self.helper.vc4d(self.helper.getObject(name).GetMg().off) for name in sph]
#        for name in sph:
#            o = self.helper.getObject(name)
#            pos=o.GetMg().off
#    #        pos=o.GetAbsPos()
#            vt.append(self.helper.vc4d(pos))
        print vt[0]
        return vt
#
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
    