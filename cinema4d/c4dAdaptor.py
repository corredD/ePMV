
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/cinema4d/c4dAdaptor.py is part of ePMV.

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
import upy
c4dHelper = upy.getHelperClass()
from ePMV.epmvAdaptor import epmvAdaptor

import c4d

from MolKit.protein import Protein,Chain
from Pmv.pmvPalettes import AtomElements
#from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
#from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
#from Pmv.pmvPalettes import Shapely
#from Pmv.pmvPalettes import SecondaryStructureType

class c4dAdaptor(epmvAdaptor):
    """
    The specific adaptor for C4D R12.
    
    from ePMV.cinema4d.c4dAdaptor import c4dAdaptor
    epmv = c4dAdaptor(debug=1)
    epmv.mv.readMolecule("/Users/ludo/blenderKTF/1CRN.pdb")
    epmv.mv.computeMSMS("1CRN")
    epmv.mv.computeMSMS("1CRN", log=1, display=True, perMol=1,surfName="MSMS-MOL1CRN")
    epmv.mv.displayCPK("1CRN",log=1,negate=False,scaleFactor = 1.0)
    ...
    """

    def __init__(self,gui=False,mv=None,debug=0):
        self.helper = c4dHelper()
        epmvAdaptor.__init__(self,mv,host='c4d',debug=debug)
        self.MAX_LENGTH_NAME = 20
        self.soft = 'c4d'
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
        self.keywords["ribcolor"]={"name":"use vertex color for ribbon geometry","value":False,"type":"checkbox"}
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
            root.MakeTag(1027093)
            self.helper.addObjectToScene(self.helper.getCurrentScene(),root)

    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self._getCurrentScene()
        if shape is None :
            circle=self.helper.Circle(name+"circle",rad=0.5)
            self._addObjectToScene(sc,circle)
        if spline is None :
            spline = self.helper.spline(name+"_spline",coords,scene=sc)
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
        for atn in list(self.AtmRadi.keys()):
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
                if self.use_instances : 
                    iMe[atn] = self.helper.setInstance("mesh_"+atn+"_"+name,baseShape)
                else :
                    iMe[atn] = self.helper.newClone("mesh_"+atn+"_"+name,basesphere)
                self.helper.scaleObj(iMe[atn],float(rad))
                #iMe[atn]=c4d.BaseObject(c4d.Osphere)
                self.helper.addObjectToScene(doc,atparent,parent=baseparent)
                self.helper.addObjectToScene(doc,iMe[atn],parent=atparent)
                if self.use_instances : 
                    iMe[atn]=atparent   
        return iMe

    def _changeColor(self,geom,colors,perVertex=True,proxyObject=True,pb=False):
        if hasattr(geom,'mesh'):
            if geom.name[:4] in ['Heli', 'Shee', 'Coil', 'Turn', 'Stra']:
                proxyObject=False       
            objToColor = geom.mesh
        elif hasattr(geom,"obj"):
            objToColor = geom.obj
        else :
            objToColor = None            
        if hasattr(geom,"name") :
            if geom.name[:4] in ['secondarystructure','Heli', 'Shee', 'Coil', 'Turn', 'Stra']:
                proxyObject=False
                if self.ribcolor :
                    proxyObject=True
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
        self.helper.changeColor(self.helper.getName(objToColor),colors,perVertex=perVertex,
                                    proxyObject=proxyObject,pb=pb)

    def _armature(self,name,atomset,coords=None,root=None,scn=None):
        scn=self.helper.getCurrentScene()
        names = None
        if coords is not None :
            c = coords    
        else :
            c = atomset.coords
            names = [x.full_name().replace(":","_") for x in atomset]
        object,bones=self.helper.armature(name,c,listeName=names,
                                          root=root,scn=scn)
        return object,bones

    def _updateArmature(self,name,atomset,coords=None,root=None,scn=None):
        scn=self.helper.getCurrentScene()
        names = None
        if coords is not None :
            c = coords    
        else :
            c = atomset.coords
            names = [x.full_name().replace(":","_") for x in atomset]
        self.helper.updateArmature(name,c,listeName=names,
                                          root=root,scn=scn)
        
    def _metaballs(self,name,coords,radius,scn=None,root=None):
        #by default we build the clouds metaballs...maybe could do on particle
        basename = name.split("_")[0] #basename form : mol.name+"_metaball"
        cloud = self.helper.getObject(name+"_cloud")
        if cloud is None :
            cloud = self.helper.PointCloudObject(name+"_cloud",
                                        vertices=coords,
                                        parent=None,atomarray=False)[0]
        metab=self.helper.create_metaballs(name,sourceObj=cloud,parent=root,
                                           coords=coords)
        return [None,metab]
        

    def _instancesAtomsSphere_full(self,name,x,iMe,scn,mat=None,scale=1.0,Res=32,
                            R=None,join=0,geom=None,dialog=None,pb=False):
        #radius made via baseMesh...
        #except for balls, need to scale?#by default : 0.3? 
        if scn == None :
            scn=self.helper.getCurrentScene()
        sphers=[]
        k=0
        n='S'
        nn='cpk'
        if name.find('balls') != (-1) : 
            n='B'
            nn='balls'
        
        if geom is not None:
            coords=geom.getVertices()
        else :
            coords=x.coords
        hiera = 'default'    
#        parent=self.findatmParentHierarchie(x[0],n,hiera) 
        mol = x[0].getParentOfType(Protein)        
        if pb :
            self.helper.resetProgressBar()
            self.helper.progressBar(progress=0,label = "creating "+name)
        for c in mol.chains:
            spher=[]
            oneparent = True 
            atoms = c.residues.atoms
            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name+"_"+nn])
            #print "finded",parent        
            for j in range(len(atoms.coords)):
                #at=res.atoms[j]
                at=atoms[j]
                radius = at.radius
#                scaleFactor=float(R)+float(radius)*float(scale)
                atN=at.name
                if atN[0] not in list(AtomElements.keys()) : atN="A"
                fullname = self.atomNameRule(at,n)
                #at.full_name().replace("'","b")+"n"+str(at.number)
                #print fullname
                atC=at.coords#at._coords[0]
                spher.append( c4d.BaseObject(c4d.Oinstance) )
                if atN[0] in iMe :
                    sm=iMe[atN[0]]
                else :
                    sm=iMe["A"]
                spher[j][1001]=sm
                #spher[j][1001]=1        
                spher[j].SetName(fullname)#.replace(":","_")
                sc = sm[905].x #radius of parent mesh
                #we can compare to at.vwdRadius
                if sc != radius :
                    print(("rad",sc,radius,at.name))
                #if sc != scaleFactor : 
#                if n=='B' :
#                    scale = 1.
#                    spher[j][905]=c4d.Vector(float((1/sc)*scale),float((1/sc)*scale),float((1/sc)*scale))                #
                spher[j].SetAbsPos(self.helper.FromVec(atC))
                texture = spher[j].MakeTag(c4d.Ttexture)
                mat = self.helper.getMaterial(atN[0])
                if mat is None :
                    self.setupMaterials()
                    mat = self.helper.getMaterial(atN[0])
                texture[1010] = mat
                #p = self.findatmParentHierarchie(at,n,hiera)
                #print "dinded",p
#                if parent != p : 
#                    cp = p
#                    oneparent = False
#                    parent = p
#                else :
                cp = parent                            
                #print "parent",cp
                self.helper.addObjectToScene(self.helper.getCurrentScene(),spher[j],parent=cp)
                self.helper.toggleDisplay(spher[j],False)
                k=k+1
                if pb :
                    self.helper.progressBar(progress=j/len(coords))
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
        vt = [self.helper.ToVec(j.GetMg().off) for j in bones]
#        for join in bones:
#            pos=join.GetMg().off
#            vt.append(self.helper.ToVec(pos))
        print(vt[0])
        return vt
    
    def updateMolAtomCoordSpline(self,mol,index=-1):
        #problem, theses are only CA
        vts = []
    #    mesh = mol.geomContainer.geoms['lines'].obj
        for ch in mol.chains:
            name=mol.name+"_"+ch.name+"spline"
            spline = self.helper.getCurrentScene().SearchObject(name)
            points = spline.GetAllPoints()
            matr= spline.GetMg()
            vt=[self.helper.ToVec(x*matr) for x in points]
            #vt = map(lambda x,m=matr: ToVec(x),points)
            #vt = [self.helper.ToVec(x) for x in points]
            vts.append(vt)
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
            deform = mesh.GetDeformMode()
            meshcache = mesh.GetDeformCache()
            if meshcache is not None:
                meshcache = mesh.GetDeformCache()
                points = meshcache.GetAllPoints()
                vt=[self.helper.ToVec(x) for x in points]
            else :
                points = mesh.GetAllPoints()
                matr= mesh.GetMg()
                vt=[self.helper.ToVec(x*matr) for x in points]
            vts.extend(vt)
        #vt = map(lambda x,m=matr: ToVec(x*m),points)
        #these are the cpk
        if hasattr(mol.geomContainer.geoms['cpk'],'obj'):
            sph = mol.geomContainer.geoms['cpk'].obj
            #each have to be translate
            [x.SetAbsPos(self.helper.FromVec(p)) for x,p in zip(sph,vts)]
            #map(lambda x,p:x.SetAbsPos(p),sph,points)
            masterCPK=sph[0].GetUp()
            if meshcache is None:
                masterCPK.SetMg(matr)
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

    def _editLines1(self,molecules,atomSets):
        scn = self.helper.getCurrentScene()
        sel=atomSets[0]
        ch={}
        mol = sel.top.uniq
        for at in sel:
            c = at.parent.parent
            if c not in ch :
                ch[c] = [[],[]]
            ch[c][0].append(at.coords)
            bonds= at.bonds
            indices = [(x.atom1._bndIndex_,
                                             x.atom2._bndIndex_) for x in bonds]
            ch[c][1].extend(indices)
        for c in ch :
            parent = self.helper.getObject(c.full_name())
            lines = self.helper.getObject(c.full_name()+'_line')
            if lines == None :
                    arr = c4d.BaseObject(c4d.Oatomarray)
                    arr.SetName(c.full_name()+'_lineds')
                    arr[1000] = 0.1 #radius cylinder
                    arr[1001] = 0.1 #radius sphere
                    arr[1002] = 3 #subdivision
                    self.helper.addObjectToScene(scn,arr,parent=parent) 
                    lines = self.helper.createsNmesh(c.full_name()+'_line',
                                                     ch[c][0],
                                                     None,ch[c][1])
                    self.helper.addObjectToScene(scn,lines[0],parent=arr)
                    mol.geomContainer.geoms[c.full_name()+'_line'] = lines
            else :
                    self.helper.updatePoly(lines,vertices=ch[c][0],faces=ch[c][1])

    def _editLines(self,molecules,atomSets):
        print "editLines"
        scn = self.helper.getCurrentScene()
        sel=atomSets[0]
        ch={}
        mol = sel[0].getParentOfType(Protein)
        v = mol.geomContainer.geoms["bonded"].getVertices()#not update ?
        f = mol.geomContainer.geoms["bonded"].getFaces()
        parent = self.helper.getObject(mol.full_name())
        lines = self.helper.getObject(mol.full_name()+'_line')
        arr = self.helper.getObject(mol.full_name()+'_lineds')
        if lines == None :
                arr = c4d.BaseObject(c4d.Oatomarray)
                arr.SetName(mol.full_name()+'_lineds')
                arr[1000] = 0.1 #radius cylinder
                arr[1001] = 0.1 #radius sphere
                arr[1002] = 3 #subdivision
                self.helper.addObjectToScene(scn,arr,parent=parent) 
                lines = self.helper.createsNmesh(mol.full_name()+'_line',
                                                 v,
                                                 None,f)
                self.helper.addObjectToScene(scn,lines[0],parent=arr)
                mol.geomContainer.geoms[mol.full_name()+'_line'] = lines
        else :
                print "what"
#                self.helper.updatePoly(lines,vertices=v,faces=f)
#                self.helper.redoPoly(lines,v,f,parent=arr)
                self.helper.updateMesh(lines,vertices=v,faces = f)


    def _editLinesWorking(self,molecules,atomSets):            
        scn = self.helper.getCurrentScene()
        for mol, atms, in map(None, molecules, atomSets):
            #check if line exist
            for ch in mol.chains:
                parent = self.helper.getObject(ch.full_name())
                lines = self.helper.getObject(ch.full_name()+'_line')
                if lines == None :
                    arr = c4d.BaseObject(c4d.Oatomarray)
                    arr.SetName(ch.full_name()+'_lineds')
                    arr[1000] = 0.1 #radius cylinder
                    arr[1001] = 0.1 #radius sphere
                    arr[1002] = 3 #subdivision
                    self.helper.addObjectToScene(scn,arr,parent=parent)                
                    bonds, atnobnd = ch.residues.atoms.bonds
                    indices = [(x.atom1._bndIndex_,
                                             x.atom2._bndIndex_) for x in bonds]
    
                    lines = self.helper.createsNmesh(ch.full_name()+'_line',
                                                     ch.residues.atoms.coords,
                                                     None,indices)
                    self.helper.addObjectToScene(scn,lines[0],parent=arr)
                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
                    #display using AtomArray
                else : #need to update
#                    self.helper._updateLines(lines, chains=ch)
                    self.helper.updatePoly(lines,vertices=ch.residues.atoms.coords)
    