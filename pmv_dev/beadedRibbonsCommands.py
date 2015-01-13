#
# $Header: /opt/cvs/python/packages/share1.5/Pmv/beadedRibbonsCommands.py,v 1.17 2010/11/11 18:05:56 sanner Exp $
#
# $Id: beadedRibbonsCommands.py,v 1.17 2010/11/11 18:05:56 sanner Exp $
#
#will try to use pyubic as self.vf.helper

## KNOWN issues
## after restoring form a session, compute->beaded Ribbon does not restore chcek button for strands
##
import numpy
import numpy.oldnumeric as Numeric
import os, sys
try :
	import tkinter
except :
    import Tkinter as tkinter
import Pmw, ImageTk

from Pmv.mvCommand import MVCommand
from ViewerFramework.VFCommand import CommandGUI
from Pmv.moleculeViewer import ICONPATH
from math import cos,sin, pi
from DejaVu.IndexedPolygons import IndexedPolygons
from DejaVu.Geom import Geom
from Pmv.extruder import ExtrudeObject, ExtrudeCirclesWithRadii
from Pmv.extruder import Sheet2D
from mglutil.util.callback import CallbackFunction
from mglutil.gui.BasicWidgets.Tk.thumbwheel import ThumbWheel
from MolKit.molecule import MoleculeSet
from MolKit.molecule import AtomSet
from Pmv.displayCommands import DisplayCommand

#event mangent
from Pmv.moleculeViewer import DeleteGeomsEvent, AddGeomsEvent, EditGeomsEvent
from mglutil.math import crossProduct,norm

def getAtsRes(atoms,listesel):
    missingAts = False
    listeCoord = []
    for astr in listesel :
        AT = atoms.objectsFromString(astr)  
        if len(AT) :
            ATcoord = Numeric.array(AT[0].coords)
            listeCoord.append(ATcoord)
        else : missingAts = True
    return listeCoord,missingAts

def ExtrudeNA(chain,name='ssSheet2D'):
    """Computes ribbons for DNA/RNA"""
    coord = []
    coord.append(chain.DNARes[0].atoms[0].coords)
    NA_type = chain.DNARes[0].type.strip()                        
    atoms = chain.DNARes[0].atoms
    missingAts = False
    normal = Numeric.array([0.,1.,0.])
    if NA_type in ['A', 'G']:
        listesel = ['N9.*','C8.*','C4.*']
        listeCoord,missingAts = getAtsRes(atoms,listesel)
        if not missingAts :
            N9 =  listeCoord[0]#Numeric.array(atoms.objectsFromString('N9.*')[0].coords)
            C8 =  listeCoord[1]#Numeric.array(atoms.objectsFromString('C8.*')[0].coords)
            C4 =  listeCoord[2]#Numeric.array(atoms.objectsFromString('C4.*')[0].coords)
            N9_C8 = C8-N9
            N9_C4 = C4-N9
            normal = Numeric.array(crossProduct(N9_C8, N9_C4, normal=True))
    else:
        listesel = ['N1.*','C2.*','C6.*']
        listeCoord = []
        listeCoord,missingAts = getAtsRes(atoms,listesel)
        if not missingAts :
            N1 =  listeCoord[0]#Numeric.array(atoms.objectsFromString('N1.*')[0].coords)
            C2 =  listeCoord[1]#Numeric.array(atoms.objectsFromString('C2.*')[0].coords)
            C6 =  listeCoord[2]#Numeric.array(atoms.objectsFromString('C6.*')[0].coords)
            N1_C2 = C2-N1
            N1_C6 = C6-N1
            normal = Numeric.array(crossProduct(N1_C2, N1_C6, normal=True))
    base_normal = Numeric.array(chain.DNARes[0].atoms[0].coords)
    coord.append((base_normal + normal).tolist())

    for res in chain.DNARes[1:]:
        normal = Numeric.array([0.,1.,0.])
        if res.atoms.objectsFromString('P.*'):
            P_coord = res.atoms.objectsFromString('P.*')[0].coords
            coord.append(P_coord)
        else: # this in case last residue does not have P
            P_coord = res.atoms[0].coords
        NA_type = res.type.strip()      
        atoms = res.atoms
        if NA_type in ['A', 'G']:
            listesel = ['N9.*','C8.*','C4.*']
            listeCoord,missingAts = getAtsRes(atoms,listesel)
            if not missingAts :
                N9 =  listeCoord[0]#Numeric.array(atoms.objectsFromString('N9.*')[0].coords)
                C8 =  listeCoord[1]#Numeric.array(atoms.objectsFromString('C8.*')[0].coords)
                C4 =  listeCoord[2]#Numeric.array(atoms.objectsFromString('C4.*')[0].coords)
                N9_C8 = C8-N9
                N9_C4 = C4-N9
                normal = Numeric.array(crossProduct(N9_C8, N9_C4, normal=True))
        else:
            listesel = ['N1.*','C2.*','C6.*']
            listeCoord = []
            listeCoord,missingAts = getAtsRes(atoms,listesel)
            if not missingAts :
                N1 =  listeCoord[0]#Numeric.array(atoms.objectsFromString('N1.*')[0].coords)
                C2 =  listeCoord[1]#Numeric.array(atoms.objectsFromString('C2.*')[0].coords)
                C6 =  listeCoord[2]#Numeric.array(atoms.objectsFromString('C6.*')[0].coords)
                N1_C2 = C2-N1
                N1_C6 = C6-N1
                normal = Numeric.array(crossProduct(N1_C2, N1_C6, normal=True))
        base_normal = Numeric.array(P_coord)
        coord.append((base_normal + normal).tolist())
        
    chain.sheet2D[name] = Sheet2D()
    chain.sheet2D[name].compute(coord, len(chain.DNARes)*(False,), 
                             width = 2.0,off_c = 0.9,offset=0.0, nbchords=4)
    chain.sheet2D[name].resInSheet = chain.DNARes

class BeadedRibbonsRegCommand(MVCommand):
    """
    Command to compute Beaded Ribbons for selected molecule(s)
    \nPackage : Pmv
    \nModule  : beadedRibbonsCommands
    \nClass   : BeadedRibbonsCommand
    \nCommand name : beadedRibbons
    """

    def __init__(self):
        MVCommand.__init__(self)
        self.master = None
        self.colors = {"helixColor1" :(1,1,1), # color of helix front faces
                       "helixColor2" :(1,0,1), # color of helix back faces
                       "helixBeadColor1" :(1,1,1),
                       "helixBeadColor2" :(1,1,1),
                       "coilColor" :(1,1,1),
                       "turnColor": (0,0,1),
                       "sheetColor1":(1,1,0),
                       "sheetColor2":(0,1,1),
                       "sheetBeadColor1":(1,1,1),
                       "sheetBeadColor2":(1,1,1)}
        self.lastNodes = None
        self.molModeVars = {}
        self.molFrames = {}
        self.strandW = [] # list of checkbuttons for strand color flipping
        self.redo = False

    def setupUndoBefore(self, nodes, **kw):
        for mol in nodes.top.uniq():
            if hasattr(mol, 'beadedRibbonParams'):
                self.addUndoCall( (MoleculeSet([mol]),),
                                  mol.beadedRibbonParams, self.name )


    def onAddCmdToViewer(self):
        self.vf.browseCommands('secondaryStructureCommands',  log=0)


    def onAddObjectToViewer(self, obj):
        #print "onAddObjectToViewer:", obj
        if self.master and self.vf.hasGui:
            if obj in self.vf.Mols:
                self.addFileProssRadioButtons(obj.name)

    def onRemoveObjectFromViewer(self, mol):
        if self.master:
            if mol.name in self.molFrames:
                f = self.molFrames.pop(mol.name)
                f.destroy()
            if mol.name in self.molModeVars:
                self.molModeVars.pop(mol.name)
            self.hide()


    def clearStrandVar(self):
        for w in self.strandW:
            w.destroy()
        self.strandW = []


    def flipStrandColor(self, molName, chainId, SSname):
        vi = self.vf.GUI.VIEWER
        f1 = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
            molName, chainId, SSname+'_faces'))
        f2 = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
            molName, chainId, SSname+'_faces2'))
        from opengltk.OpenGL import GL
        color1 = f1.materials[GL.GL_FRONT].prop[1].copy()
        color2 = f2.materials[GL.GL_FRONT].prop[1].copy()
        f1.Set(materials = color2)
        f2.Set(materials = color1)
        
        
    def __call__(self, nodes, **kw):
        """None<-beadedRibbons(nodes, **kw)
        \nRequired Arguments:\n
            \nnodes  ---  current selection
        \nOptional Arguments:\n
             \nquality --- number of segments per residue (default 12)
             \ntaperLength --- number of points needed to close (taper off) the ribbon (default quality/2)
             \nhelixBeaded --- if set to True - add beads to helix (default True)
             \nhelixCylinder --- if set to True - no beads, helix replace by cylinder (default False)
             \nhelixWidth ---(default 1.6)
             \nhelixThick --- if set to True - add thikness to helix (default True)
             \nhelixThickness --- helix thickness (default.20 )
             \nhelixBeadRadius --- radius of helix beads(default 0.32)
             \nhelixColor1 --- helix outside color(default(1,1,1)
             \nhelixColor2 --- helix inside color (default1,0,1)
             \nhelixBeadColor1 --- color of beads on one side of helix (default (1,1,1))
             \nhelixBeadColor2  --- color of beads on the other side of helix (default (1,1,1) )
             
             \ncoilRadius --- coil radius(default 0.2)
             \ncoilColor --- coil color (default (1,1,1))
             
             \nturnRadius --- turn radius (default 0.2)
             \nturnColor --- turn color (default (0,0,1))
             
             \nsheetBeaded --- (if set to True - add beads to sheet (default True)
             \nsheetWidth --- width of sheet(default 1.6)
             \nsheetBodyStartScale --- (default 0.4)
             \nsheetThick --- if set to True - add thikness to sheet(default True)
             \nsheetThickness --- sheet thickness (default .20)
             \nsheetBeadRadius --- radius of sheet's beads (default 0.32)
             \nsheetColor1 --- sheet outside color (default (1,1,0) )
             \nsheetColor2 --- sheet inside color (default (0,1,1) )
             \nsheetBeadColor1 --- color of beads  on one side of sheet (default (1,1,1) )
             \nsheetBeadColor2 --- color of beads on the other side of beads (default (1,1,1) )
             \nsheetArrowhead --- if set to True - add arrows to sheet(default True)
             \nsheetArrowheadWidth --- width of sheet's arrow (default 2.0)
             \nsheetArrowHeadLength --- length of sheet's arrow (default 8
        """
        nodes = self.vf.expandNodes(nodes)
        if not nodes: return
        self.doitWrapper(nodes, **kw)
        self.lastNodes = nodes


    def doit(self, nodes,
             quality = 12,  # number of segments per residue
             taperLength = None, # default to quality/2
             taperType = "sin", #detault is sinusoidale.
             helixBeaded = True,
             helixCylinder = False,
             helixWidth = 1.6,
             helixThick = True,
             helixThickness = .20,
             helixBeadRadius = 0.32,
             helixColor1 = (1,1,1), # color of helix front faces
             helixColor2 = (1,0,1), # color of helix front faces
             helixBeadColor1 = (1,1,1),
             helixBeadColor2 = (1,1,1),
             helixSideColor = (0,1,0),
             coilRadius = 0.2,
             coilColor = (1,1,1),
             
             turnRadius = 0.2,
             turnColor = (0,0,1),
             
             sheetBeaded = True,
             sheetWidth = 1.6,
             sheetBodyStartScale = 0.4,
             sheetThick = True,
             sheetThickness = .20,
             sheetBeadRadius = 0.32,
             sheetColor1 = (1,1,0),
             sheetColor2 = (0,1,1),
             sheetBeadColor1 = (1,1,1),
             sheetBeadColor2 = (1,1,1),
             sheetSideColor = (0,1,0),
             sheetArrowhead = True,
             sheetArrowheadWidth = 2.0,
             sheetArrowHeadLength = 8):

        # build dict of parameters used to restore in session and undo
        if helixCylinder :
            helixBeaded = False
        params = {
            'quality':quality,
            'taperLength':taperLength,
            'taperType':taperType,
            'helixBeaded':helixBeaded,
            'helixCylinder':helixCylinder,
            'helixWidth':helixWidth,
            'helixThick':helixThick,
            'helixThickness':helixThickness,
            'helixBeadRadius':helixBeadRadius,
            'helixColor1':helixColor1,
            'helixColor2':helixColor2,
            'helixBeadColor1':helixBeadColor1,
            'helixBeadColor2':helixBeadColor2,             
            'helixSideColor':helixSideColor,             
            'coilRadius':coilRadius,
            'coilColor':coilColor,
            'turnRadius':turnRadius,
            'turnColor':turnColor,
            'sheetBeaded':sheetBeaded,
            'sheetWidth':sheetWidth,
            'sheetBodyStartScale':sheetBodyStartScale,
            'sheetThick':sheetThick,
            'sheetThickness':sheetThickness,
            'sheetBeadRadius':sheetBeadRadius,
            'sheetColor1':sheetColor1,
            'sheetColor2':sheetColor2,
            'sheetBeadColor1':sheetBeadColor1,
            'sheetBeadColor2':sheetBeadColor2,
            'sheetSideColor':sheetSideColor,             
            'sheetArrowhead':sheetArrowhead,
            'sheetArrowheadWidth':sheetArrowheadWidth,
            'sheetArrowHeadLength':sheetArrowHeadLength,
        }
        vi = None
        if self.vf.hasGui :
            vi = self.vf.GUI.VIEWER
            
        helixBeadRadius *=.25
        sheetBeadRadius *=.25
        
        pi2 = pi*.5
            
        ## create Circle shapes for beads, Rutns and Coils
        from DejaVu.Shapes import Circle2D
        circleHB = Circle2D( helixBeadRadius )
        circleSB = Circle2D( sheetBeadRadius )
        circleT = Circle2D( turnRadius )
        circleC = Circle2D( coilRadius )

        # these values are ignored
        gapEnd = gapBeg = 2
        frontcap = endcap = 0
        print ("build beadedRibon")
        for mol in nodes.top.uniq():
            if not hasattr(self.vf, 'secondarystructureset') or self.redo:
                # FIXME use self.molModVars to use PROSS or file info for SS
                if mol.name not in self.molModeVars:
                    if mol.parser.hasSsDataInFile():
                        mod = "From File"
                    else:
                        mod = "From Pross"
                else:
                    mod = self.molModeVars[mol.name].get()
                print ("recompute",mod)
                self.vf.computeSecondaryStructure(
                    mol, molModes={'%s'%mol.name:mod}, topCommand=0)

            # check mol.strandVar
            createStrandVar = False
            if not hasattr(mol, 'strandVar'):
                mol.strandVar = {}
                createStrandVar = True
            elif len(mol.strandVar) > 0:
                for chain in mol.chains:
                    if createStrandVar is False:
                        for SS in enumerate(chain.secondarystructureset):
                            if SS.__class__.__name__=='Strand':
                                #print SS, mol.strandVar.has_key('%s%s%s'%(mol.name, chain.id,SS.name))
                                if '%s%s%s'%(mol.name, chain.id,SS.name) not in mol.strandVar:
                                    mol.strandVar = {}
                                    createStrandVar = True
                                    break

            mol.beadedRibbonParams = params
            # create a master geometry for the beaded ribbon
#            molMaster = Geom('beadedRibbon')
#            if self.vf.hasGui :
#                vi.AddObject(molMaster, parent=mol.geomContainer.geoms['master'])
#            else :
#                mol.geomContainer.geoms['master'].children.append(molMaster)
#                molMaster.parent = mol.geomContainer.geoms['master']
            col = row = 0

            for chain in mol.chains:
                chainMaster=self.vf.helper.getObject(mol.name+chain.name+"_beadedRibbon")
                parent = mol.geomContainer.masterGeom.chains_obj[chain.name]
                #not the mastergeom mol.geomContainer.geoms['master'].obj
                if chainMaster is None:
                    chainMaster=self.vf.helper.newEmpty(mol.name+chain.name+"_beadedRibbon")
                    self.vf.helper.addObjectToScene(None,chainMaster,parent=parent)
                # create a master geometry for the beaded ribbon ALREADY CREATE line 263 ?
#                molMaster = Geom('beadedRibbon')
#                if self.vf.hasGui :
#                    vi.AddObject(molMaster, parent=mol.geomContainer.geoms['master'])
#                else :
#                    mol.geomContainer.geoms['master'].children.append(molMaster)
#                    molMaster.parent = mol.geomContainer.geoms['master']
                if not hasattr(chain, 'sheet2D') or \
                   'beadedRibbonSheet' not in chain.sheet2D or self.redo:
                    if chain.ribbonType()=='NA':
                        chain.sheet2D={}
                        ExtrudeNA(chain,name='beadedRibbonSheet')
                    else :
                        self.vf.computeSheet2D(chain, 'beadedRibbonSheet', 'CA', 'O',
                                       buildIsHelix=1, nbrib=2,
                                       nbchords=quality, width=1.0, offset=1.2,
                                       topCommand=0)
                sheet = chain.sheet2D['beadedRibbonSheet']
    
                # create a master geometry this chain
#                chainMaster = Geom('chain%s'%chain.id)
#                if self.vf.hasGui :
#                    vi.AddObject(chainMaster, parent=molMaster)
#                else :
#                    molMaster.children.append(chainMaster)
#                    chainMaster.parent = molMaster                 
                # path is at the center of the 2D sheet
                path = sheet.path.copy()
                # n1 is normal to path and in the plane of the 2D sheet
                n1 = sheet.normals
                # b1 is orthogonal to 2D sheet plane
                b1 = sheet.binormals
                # compute Gaussian transport matrices for path 3D
                matrix = sheet.buildTransformationMatrix(path, n1, b1)
    
                # make a copy of the 3D path on each edge of the 2D sheet
                path1 = sheet.smooth[0,:,:3].copy()
                path2 = sheet.smooth[1,:,:3].copy()
                matrix1 = sheet.buildTransformationMatrix(path1, n1, b1)
                matrix2 = sheet.buildTransformationMatrix(path2, n1, b1)
    
                # set variable used to find portions of path 3d and 2D faces
                chords = sheet.chords
                lastResIndex = len(sheet.resInSheet)-1
                sheet.resInSheet.resIndInSheet = list(range(lastResIndex+1))
                lengthPath = len(sheet.path)
    
                # set length of taper in number of points along the path
                if taperLength is None:
                    c2 = int(chords/2)
                else:
                    c2 = int(taperLength)
    
            ##
            ## loop over SS elements and taper path1 and path2 at beginning and end
            ## by moving points in path1 and path2
            ##
                for i, SS in enumerate(chain.secondarystructureset):
                    # get start and end index into path for first residue in SSelement
                    start, end1 = self.getResPts(
                        SS.start.resIndInSheet, chords, lastResIndex, lengthPath)
                    # get start and end index into path for last residue in SSelement
                    start1, end = self.getResPts(
                        SS.end.resIndInSheet, chords, lastResIndex, lengthPath)
    
                    # the first point in path is way off so we ignore it and start
                    # at the CA of the first residue
                    if start == 0: start=1
    
                    sstype = SS.__class__.__name__
                    if chain.ribbonType()=='NA':
                        sstype = 'Helix'
                    ## handle Helices and strand
                    if sstype in ['Strand', 'Helix']:
    
                        # change path1 and path2 to taper begin and end
                        p1 = path1[start:end]
                        p2 = path2[start:end]
                        p = path[start:end]
    
                        ##
                        ## Helix
                        ##
                        if sstype =='Helix':
                            width = helixWidth
                            endSca = 1.0 # this measn no arrow head at the end
                            # tapper begin: first c2 points
                            # 
                            for i in range(c2):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                if taperType == "sin" :
                                    q = sin((i/float(c2))*pi2)*width
                                elif taperType == "cos" :
                                    q = cos(pi2-(i/float(c2))*pi2)*width
                                elif taperType == "linear":
                                    q = (i/float(c2))*width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # scale helix to width
                            length = (len(p)-(2*c2))-1
                            for i in range(c2, c2+length+1):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                q = width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # tapper end: last c2 points
                            for i in range(c2):
                                # tapper end
                                i1 = -i-1
                                x1,y1,z1 = p1[i1]
                                x2,y2,z2 = p2[i1]
                                x,y,z = p[i1]
                                if taperType == "sin" :
                                    q = endSca*sin((i/float(c2))*pi2)*width
                                elif taperType == "cos" :
                                    q = endSca*cos(pi2-(i/float(c2))*pi2)*width
                                elif taperType == "linear":
                                    q = endSca*(i/float(c2))*width
                                #print 'End', i1, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i1] = (p[i1][0] + vx1, p[i1][1]+vy1, p[i1][2]+vz1)
                                p2[i1] = (p[i1][0] + vx2, p[i1][1]+vy2, p[i1][2]+vz2)
    
                        ##
                        ## STRAND
                        ##
                        else:                      
                            width = sheetWidth
                            if sheetArrowhead:
                                endSca = sheetArrowheadWidth
                            else:
                                endSca = 1.0
    
                            # start of sheet is only sheetBodyStartScale% width
                            sca = sheetBodyStartScale
    
                            # tapper begin to sheetBodyStartScale% width
                            for i in range(c2):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                if taperType == "sin" :
                                    q = sin((i/float(c2))*pi2)*sca*width
                                elif taperType == "cos" :
                                    q = cos(pi2-(i/float(c2))*pi2)*sca*width
                                elif taperType == "linear":
                                    q = (i/float(c2))*sca*width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                #print 'Sheet start', i, q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # scale path from sheetBodyStartScale% to 100% width
                            length = len(p)-c2-sheetArrowHeadLength-1#length = (len(p)-(2*c2))-1
                            #print SS, len(p), c2, length
                            for i in range(c2, c2+length+1):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                q = (sca + ((1.0-sca)*(i-c2)/length))*width
                                #print 'Sheet body', i, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # tapper end from 100% width
                            for i in range(sheetArrowHeadLength):
                                i1 = -i-1
                                x1,y1,z1 = p1[i1]
                                x2,y2,z2 = p2[i1]
                                x,y,z = p[i1]
                                if taperType == "sin" :
                                    q = endSca*sin((i/float(sheetArrowHeadLength))*pi2)*width
                                elif taperType == "cos" :
                                    q = endSca*cos(pi2-(i/float(sheetArrowHeadLength))*pi2)*width
                                elif taperType == "linear":
                                    q = endSca*(i/float(sheetArrowHeadLength))*width
                                #print 'Sheet End', i1, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i1] = (p[i1][0] + vx1, p[i1][1]+vy1, p[i1][2]+vz1)
                                p2[i1] = (p[i1][0] + vx2, p[i1][1]+vy2, p[i1][2]+vz2)
                            #p1[i1-1] = p1[i1]
                            #p2[i1-1] = p2[i1]   
                        # update Gaussian transport matrices for path1 and path2
                        # for this SS element
                        matrix1[start:end] = sheet.buildTransformationMatrix(
                                p1, n1[start:end], b1[start:end])
                        matrix2[start:end] = sheet.buildTransformationMatrix(
                                p2, n1[start:end], b1[start:end])
    
                ##
                ## perform the extrusion using path2, path and path1
                ##
                for nss, SS in enumerate(chain.secondarystructureset):
                    start, end1 = self.getResPts(
                        SS.start.resIndInSheet, chords, lastResIndex, lengthPath)
                    start1, end = self.getResPts(
                        SS.end.resIndInSheet, chords, lastResIndex, lengthPath)
    
                    if start==0: start=1 # skip first point because if it far away
                    p1 = path1[start:end]
                    p2 = path2[start:end]
                    pol2 = pol3 = None
    
                    sstype = SS.__class__.__name__
                    if chain.ribbonType()=='NA':
                        sstype = 'Helix'                    
                    if sstype in ['Strand', 'Helix']:
                        #print SS, start, end
                        if sstype=='Helix': prevRad = helixBeadRadius
                        else:prevRad = sheetBeadRadius
    
                        if (sstype=='Helix' and helixBeaded) or \
                               (sstype=='Strand' and sheetBeaded):
                            if sstype=='Helix':
                                color1 = helixBeadColor1
                                color2 = helixBeadColor2
                                circle = circleHB
                            else:
                                color1 = sheetBeadColor1
                                color2 = sheetBeadColor2
                                circle = circleSB
    
                            extruder1 = ExtrudeObject(p1, matrix1[start:end],
                                                      circle, cap1=1, cap2=1)
    
                            #check if the geom already exist if yes update if no create
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_edge1'
                            edge1 = self.vf.helper.getObject(name)
                            if edge1 is None :
                                edge1 = self.vf.helper.createsNmesh(name,
                                        extruder1.vertices,extruder1.vnormals,extruder1.faces,
                                        color=color1)
                                self.vf.helper.addObjectToScene(None,edge1[0],parent=chainMaster)
                            else :
                                print ("update1")
                                self.vf.helper.updateMesh(edge1,vertices=extruder1.vertices,
                                                          faces = extruder1.faces)
                                matname = "mat_"+self.vf.helper.getName(edge1)
                                self.vf.helper.colorMaterial(matname, color1) 
                                self.vf.helper.toggleDisplay(edge1,True)                                
#                            edge1 = IndexedPolygons(
#                                SS.name+'_edge1', vertices=extruder1.vertices,
#                                faces=extruder1.faces, vnormals=extruder1.vnormals,
#                                inheritMaterial=0, materials=[color1,])
#                            if self.vf.hasGui :
#                                vi.AddObject(edge1, parent=chainMaster)
#                            else :
#                                chainMaster.children.append(edge1)
#                                edge1.parent = chainMaster
                            extruder2 = ExtrudeObject(p2, matrix2[start:end],
                                                  circle, cap1=1, cap2=1)
                                                  
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_edge2'
                            edge2 = self.vf.helper.getObject(name)
                            if edge2 is None :
                                edge2 = self.vf.helper.createsNmesh(name,
                                        extruder2.vertices,extruder2.vnormals,extruder2.faces,
                                        color=color2)
                                self.vf.helper.addObjectToScene(None,edge2[0],parent=chainMaster)
                            else :
                                print ("update2")
                                self.vf.helper.updateMesh(edge2,vertices=extruder2.vertices,
                                                          faces = extruder2.faces)
                                matname = "mat_"+self.vf.helper.getName(edge2)
                                self.vf.helper.colorMaterial(matname, color2)
                                self.vf.helper.toggleDisplay(edge2,True)                                
#                            edge2 = IndexedPolygons(
#                                SS.name+'_edge2', vertices=extruder2.vertices,
#                                faces=extruder2.faces, vnormals=extruder2.vnormals,
#                                inheritMaterial=0, materials=[color2,])
#                            if self.vf.hasGui :
#                                vi.AddObject(edge2, parent=chainMaster)
#                            else :
#                                chainMaster.children.append(edge2)
#                                edge2.parent = chainMaster      
                        else:
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_edge1'
                            edge1 = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(edge1,False)
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_edge2'
                            edge2 = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(edge2,False)
#                            if self.vf.hasGui : 
#                                obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                        mol.name, chain.id, SS.name+'_edge1'))
#                                if obj: vi.RemoveObject(obj)
#                                obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                        mol.name, chain.id, SS.name+'_edge2'))
#                                if obj: vi.RemoveObject(obj)            
#                            else :
#                                obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],
#                                        '%s|beadedRibbon|chain%s|%s'%(
#                                        mol.name, chain.id, SS.name+'_edge1'))
#                                if obj: self.vf.RemoveObject_noGui(obj)
#                                obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon|chain%s|%s'%(
#                                        mol.name, chain.id, SS.name+'_edge2'))
#                                if obj: self.vf.RemoveObject_noGui(obj)                                            
                        polv = path1.tolist()+path2.tolist()
                        polf = sheet.faces2D[start:end-1].tolist()
                        poln = numpy.array(sheet.binormals.tolist()+
                                           sheet.binormals.tolist())
                        if sstype=='Helix' and helixCylinder: 
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces'
                            pol = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(pol,False)                            
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces2'
                            pol2 = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(pol2,False)
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_sides'
                            pol3 = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(pol3,False)     
                            
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_cyl'
                            pol= self.vf.helper.getObject(name)
                            if pol is None:
#                                p = path[start:end]
                                pol=self.vf.helper.oneCylinder(name,path[start],path[end-1],
                                                               color=helixColor1,parent=chainMaster,
                                                               )
                            else :
                                print ("update3")
                                self.vf.helper.updateOneCylinder(name,path[start],path[end-1],
                                                               color=helixColor1)
                                self.vf.helper.toggleDisplay(pol,True)                                                                
                           
                        elif sstype=='Helix' and not helixCylinder:
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_cyl'
                            cyl = self.vf.helper.getObject(name)
                            self.vf.helper.toggleDisplay(cyl,False)     
                            
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces'
                            pol = self.vf.helper.getObject(name)
                            if pol is None:
                                pol = self.vf.helper.createsNmesh(name,
                                        polv,None,polf,
                                        color=helixColor1)
                                self.vf.helper.addObjectToScene(None,pol[0],parent=chainMaster)
                                pol = pol[0]
                            else :
                                print ("update4")
                                self.vf.helper.updateMesh(pol,vertices=polv,
                                                          faces = polf)
                                matname = "mat_"+self.vf.helper.getName(pol)
                                self.vf.helper.colorMaterial(matname, helixColor1)
#                            pol = IndexedPolygons(
#                                    SS.name+chain.id+'_faces', vertices=polv,
#                                    vnormals=poln, faces=polf,
#                                    inheritCulling=False, culling='None')
                            # check face normal to make sure back faces are inside
                            mid = int(start + (end-start)/2)
                            x1,y1,z1 = path[mid]
                            x2,y2,z2 = path[mid+1]
                            dbase = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) + (z2-z1)*(z2-z1)
    
                            x1,y1,z1 = path[mid]+poln[mid]
                            x2,y2,z2 = path[mid+1]+poln[mid+1]
                            dend = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) + (z2-z1)*(z2-z1)
    
                            if dbase>dend:
                               #print 'flip faces for', SS
                               fa = [ [f[3], f[2], f[1], f[0]] for f in polf ]
                               vn = numpy.array([ -v for v in poln ])
                               polf = fa
                            else:
                                vn = poln
    
                            if  helixThick:
                                polv = numpy.array(polv)
                                polv1 = polv + vn*helixThickness*.5
                                polv2 = polv - vn*helixThickness*.5
    
                                polf2 = [ [f[3], f[2], f[1], f[0]] for f in polf ]
                                
                                self.vf.helper.updateMesh(pol,vertices=polv1,
                                                          faces = polf)
                                #pol.Set(vertices=polv1, faces=polf, culling='back',
                                #        inheritMaterial=0, materials=[helixColor1,],
                                #        vnormals=vn)
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces2'
                                pol2 = self.vf.helper.getObject(name)
                                if pol2 is None:
                                    pol2 = self.vf.helper.createsNmesh(name,
                                            polv2,None,polf2,
                                            color=helixColor2)
                                    self.vf.helper.addObjectToScene(None,pol2[0],parent=chainMaster)
                                else :
                                    print ("update5")
                                    self.vf.helper.updateMesh(pol2,vertices=polv2,
                                                              faces = polf2)
                                    matname = "mat_"+self.vf.helper.getName(pol2)
                                    self.vf.helper.colorMaterial(matname, helixColor2)
                                    self.vf.helper.toggleDisplay(pol2,True)
                                #pol2 = IndexedPolygons(
                                #        SS.name+'_faces2', vertices=polv2,
                                #        faces=polf2, inheritCulling=False,
                                #        culling='back', inheritMaterial=0,
                                #        materials=[helixColor2,], vnormals=-vn)
    
                                # create sides of core
                                polv3 = polv1.tolist()+polv2.tolist()
                                l1 = len(polv1)
                                a = int(min(polf[0][0], polf[0][-1]))
                                b = int(max(polf[-1][0], polf[-1][-1]))
                                if dbase>dend:
                                    polf31 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]
                                else:
                                    polf31 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                a = int(min(polf[0][1], polf[0][2]))
                                b = int(max(polf[-1][1], polf[-1][2]))
                                if dbase>dend:
                                    polf32 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                else:
                                    polf32 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_sides'
                                pol3 = self.vf.helper.getObject(name)
                                if pol3 is None:
                                    pol3 = self.vf.helper.createsNmesh(name,
                                            polv3,None,polf31+polf32,
                                            color=helixSideColor)
                                    self.vf.helper.addObjectToScene(None,pol3[0],parent=chainMaster)
                                else :
                                    print ("update6")
                                    self.vf.helper.updateMesh(pol3,vertices=polv3,
                                                              faces = polf31+polf32)
                                    matname = "mat_"+self.vf.helper.getName(pol3)
                                    self.vf.helper.colorMaterial(matname, helixSideColor)
                                    self.vf.helper.toggleDisplay(pol3,True)
                                #pol3 = IndexedPolygons(
                                #        SS.name+'_sides', vertices=polv3,
                                #        faces=polf31+polf32, inheritCulling=False,
                                #        culling='back', inheritMaterial=0,
                                #        materials=[(0,1,0),])
    
                            else:
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces2'
                                pol2 = self.vf.helper.getObject(name)
                                self.vf.helper.toggleDisplay(pol2,False)
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_sides'
                                pol3 = self.vf.helper.getObject(name)
                                self.vf.helper.toggleDisplay(pol3,False)
                                
                                #pol.Set(inheritMaterial=0, materials=[helixColor1,])
                                #pol.Set(inheritMaterial=0,
                                #        materials=[helixColor2,], polyFace='back')
#                                if self.vf.hasGui :
#                                    obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_faces2'))
#                                    if obj: vi.RemoveObject(obj)
#                                    obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_sides'))
#                                    if obj: vi.RemoveObject(obj)
#                                else :
#                                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_faces2'))
#                                    if obj: self.vf.RemoveObject_noGui(obj)
#                                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_sides'))
#                                    if obj: self.vf.RemoveObject_noGui(obj)                                            
   
                        else: # strand
                            name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces'
                            pol = self.vf.helper.getObject(name)
                            if pol is None:
                                pol = self.vf.helper.createsNmesh(name,
                                        polv,None,polf,
                                        color=helixColor1)
                                self.vf.helper.addObjectToScene(None,pol[0],parent=chainMaster)
                                pol = pol[0]
                            else :
                                print ("update7")
                                self.vf.helper.updateMesh(pol,vertices=polv,
                                                          faces = polf)
                                matname = "mat_"+self.vf.helper.getName(pol)
                                self.vf.helper.colorMaterial(matname, sheetColor1)
                        
                            #pol = IndexedPolygons(
                            #        SS.name+'_faces', vertices=polv,
                            #        faces=polf, inheritCulling=False,
                            #        culling='None')
    
                            if sheetThick:
                                polv = numpy.array(polv)
                                polv1 = polv + poln*sheetThickness*.5
                                polv2 = polv - poln*sheetThickness*.5
    
                                polf2 = [ [f[3], f[2], f[1], f[0]] for f in polf ]

                                self.vf.helper.updateMesh(pol,vertices=polv1,
                                                          faces = polf)
                                #pol.Set(vertices=polv1, faces=polf, culling='back',
                                #        inheritMaterial=0, materials=[sheetColor1,],
                                #        vnormals=poln)
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces2'
                                pol2 = self.vf.helper.getObject(name)
                                if pol2 is None:
                                    pol2 = self.vf.helper.createsNmesh(name,
                                            polv2,None,polf2,
                                            color=sheetColor2)
                                    self.vf.helper.addObjectToScene(None,pol2[0],parent=chainMaster)
                                else :
                                    print ("update8")
                                    self.vf.helper.updateMesh(pol2,vertices=polv2,
                                                              faces = polf2)
                                    matname = "mat_"+self.vf.helper.getName(pol2)
                                    self.vf.helper.colorMaterial(matname, sheetColor2)
                                    self.vf.helper.toggleDisplay(pol2,True)

                                #pol2 = IndexedPolygons(
                                #        SS.name+'_faces2', vertices=polv2,
                                #        faces=polf2, inheritCulling=False,
                                #        culling='back', inheritMaterial=0,
                                #        materials=[sheetColor2,], vnormals=-poln)
                                # create sides of core
                                polv3 = polv1.tolist()+polv2.tolist()
                                l1 = len(polv1)
                                a = int(min(polf[0][0], polf[0][-1]))
                                b = int(max(polf[-1][0], polf[-1][-1]))
                                polf31 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                a = int(min(polf[0][1], polf[0][2]))
                                b = int(max(polf[-1][1], polf[-1][2]))
                                polf32 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]

                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_sides'
                                pol3 = self.vf.helper.getObject(name)
                                if pol3 is None:
                                    pol3 = self.vf.helper.createsNmesh(name,
                                            polv3,None,polf31+polf32,
                                            color=sheetSideColor)
                                    self.vf.helper.addObjectToScene(None,pol3[0],parent=chainMaster)
                                else :
                                    print ("update9")
                                    self.vf.helper.updateMesh(pol3,vertices=polv3,
                                                              faces = polf31+polf32)
                                    matname = "mat_"+self.vf.helper.getName(pol3)
                                    self.vf.helper.colorMaterial(matname, sheetSideColor)
                                    self.vf.helper.toggleDisplay(pol3,True)

                                #pol3 = IndexedPolygons(
                                #        SS.name+'_sides', vertices=polv3,
                                #        faces=polf31+polf32, inheritCulling=False,
                                #        culling='back', inheritMaterial=0,
                                #        materials=[(0,1,0),])
    
                            else:
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_faces2'
                                pol2 = self.vf.helper.getObject(name)
                                self.vf.helper.toggleDisplay(pol2,False)
                                name = mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")+'_sides'
                                pol3 = self.vf.helper.getObject(name)
                                self.vf.helper.toggleDisplay(pol3,False)
#                               
#                                pol.Set(inheritMaterial=0, materials=[sheetColor1,])
#                                pol.Set(inheritMaterial=0, materials=[sheetColor2,],
#                                        polyFace='back')
#                                if self.vf.hasGui:
#                                    obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_faces2'))
#                                    if obj: vi.RemoveObject(obj)
#                                    obj = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_sides'))
#                                    if obj: vi.RemoveObject(obj)
#                                else :
#                                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_faces2'))
#                                    if obj: self.vf.RemoveObject_noGui(obj)
#                                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon|chain%s|%s'%(
#                                            mol.name, chain.id, SS.name+'_sides'))
#                                    if obj: self.vf.RemoveObject_noGui(obj)                                            
    
#                        if self.vf.hasGui:
#                            vi.AddObject(pol, parent=chainMaster)
#                        else :
#                            chainMaster.children.append(pol)
#                            pol.parent = chainMaster
#                        if pol2:
#                            if self.vf.hasGui:
#                                vi.AddObject(pol2, parent=chainMaster)
#                            else :
#                                chainMaster.children.append(pol2)
#                                pol2.parent = chainMaster                            
#                        if pol3:
#                            if self.vf.hasGui:
#                                vi.AddObject(pol3, parent=chainMaster)
#                            else :
#                                chainMaster.children.append(pol3)
#                                pol3.parent = chainMaster    
                        if SS.__class__.__name__=='Strand':
                            # create widget to flip color for strand
                            if self.vf.hasGui:
                                if createStrandVar:
                                    v = tkinter.IntVar()
                                    if hasattr(mol, 'strandVarValue'):
                                        v.set(mol.strandVarValue['%s%s%s'%(mol.name, chain.id,SS.name)])
                                    else:
                                        v.set(0)
                                    mol.strandVar['%s%s%s'%(mol.name, chain.id,SS.name)] = v
                                else:
                                    v = mol.strandVar['%s%s%s'%(mol.name, chain.id,SS.name)]
                                
                                cb = CallbackFunction(self.flipStrandColor, mol.name, chain.id, SS.name)
                                if v.get():
                                    cb()
    
                                if hasattr(self, 'notebook'):
                                    page = self.notebook.page('Strand Edit')
                                    #print 'FUGUO widget',  '%s_%s_%s'%(mol.name, chain.id, SS.name)
                                    w = tkinter.Checkbutton(
                                        page, variable=v, text='%s_%s_%s'%(
                                            mol.name, chain.id, SS.name),
                                        command=cb)
                                    w.grid(column=col, row=row)
                                    col+=1
                                    if col%3==0:
                                        col = 0
                                        row += 1
                                    self.strandW.append(w)
    
                    elif sstype in ['Coil', 'Turn']:
    
                        if sstype =='Coil':
                            color = coilColor
                            circle = circleC
                            radii = [coilRadius]*int(end-start)
                            radius = coilRadius
                        else:
                            color = turnColor
                            circle = circleT
                            radii = [turnRadius]*int(end-start)
                            radius = turnRadius
    
                        # find radius of previous element
                        if SS==chain.secondarystructureset[0]:
                            startRad = radius
                        else:
                            startRad = prevRad
    
                        if SS==chain.secondarystructureset[-1]:
                            endRad = radius
                        else:
                            nextss = chain.secondarystructureset[nss+1]
                            nextsstype = nextss.__class__.__name__
                            if chain.ribbonType()=='NA':
                                nextsstype = 'Helix'                    
                            
                            if nextsstype=='Helix':
                                endRad = helixBeadRadius
                            elif nextsstype=='Strand':
                                endRad = sheetBeadRadius
                            elif nextsstype=='Turn':
                                endRad = turnRadius
                            elif nextsstype=='Coil':
                                endRad = coilRadius

                        deltaRad1 = radius-startRad
                        deltaRad2 = radius-endRad
    
                        for i in range(int(c2)):
                            radii[i] = startRad + deltaRad1*(i/float(c2))
                            radii[-i-1] = endRad + deltaRad2*(i/float(c2))
    
                        extruder = ExtrudeCirclesWithRadii(
                                path[start:end], matrix[start:end],
                                radii, cap1=1, cap2=1)
                        name = "b"+mol.name+"_"+chain.name+"_"+SS.name.replace("Nucleic","")
                        tube = self.vf.helper.getObject(name)
#                        print tube
                        if tube is None:
                            tube = self.vf.helper.createsNmesh(name,
                                    extruder.vertices,extruder.vnormals,extruder.faces,
                                    color=color)
                            self.vf.helper.addObjectToScene(None,tube[0],parent=chainMaster)
                        else :
                            print ("tube")
                            self.vf.helper.updateMesh(tube,vertices=extruder.vertices,
                                                      faces = extruder.faces)
                            matname = "mat_"+self.vf.helper.getName(tube)
                            self.vf.helper.colorMaterial(matname, color)
                            #self.vf.helper.toggleDisplay(tube,True)
                        
#                        tube = IndexedPolygons(
#                                SS.name, vertices=extruder.vertices,
#                                faces=extruder.faces, vnormals=extruder.vnormals,
#                                inheritMaterial=0, materials=[color,])
#                        if self.vf.hasGui:
#                            vi.AddObject(tube, parent=chainMaster)
#                        else :
#                            chainMaster.children.append(tube)
#                            tube.parent = chainMaster
                        prevRad = endRad
    

        setOn = AtomSet([])
        setOff = AtomSet([])        
        print ("dispatch Event")
        if self.createEvents:
            event = EditGeomsEvent(
            'bead', [nodes,[params,]],
                                    setOn=setOn, setOff=setOff)
            self.vf.dispatchEvent(event)


    def getResPts(self, residueindex, chords, lastResIndex, lengthPath):
        """ return the index of the first and the last point in the
        Sheet2D.path for the residue whose index is specified"""
        # a residue is represented in the path3D by chords points.
        # first residue represented by nbchords/2 + 1
        # last residue represented by nbchords+nbchords/2
        # all other by nbchords.
        if residueindex == 0:
            fromPts = 0
            toPts = chords/2 + 2

        elif residueindex == lastResIndex:
            fromPts = (residueindex-1) * chords + chords/2+1
            toPts = lengthPath-1

        else:
            fromPts = (residueindex-1) * chords + chords/2+1
            toPts = fromPts + chords +1

        toPts = toPts#-self.gapEnd
        fromPts = fromPts# + self.gapBeg
        return fromPts,toPts


    def rebuild(self, event=None):
        quality = self.qualityw.get()
        taperLength = self.taperLengthw.get()

        helixBeaded = self.helixBeadedvar.get()
        helixWidth = self.helixWidthw.get()
        helixBeadRadius = self.helixBeadRadiusw.get()
        helixThick = self.helixThickvar.get()
        helixThickness = self.helixThicknessw.get()

        sheetBeaded = self.sheetBeadedvar.get()
        sheetThick = self.sheetThickvar.get()
        sheetThickness = self.sheetThicknessw.get()
        sheetWidth = self.sheetWidthw.get()
        sheetBodyStartScale = self.sheetBodyStartScalew.get()
        sheetBeadRadius = self.sheetBeadRadiusw.get()
        sheetArrowhead = self.sheetArrowheadvar.get()
        sheetArrowheadWidth = self.sheetArrowheadWidthw.get()
        sheetArrowHeadLength = self.sheetArrowHeadLengthw.get()

        coilRadius = self.coilRadiusw.get()
        turnRadius = self.turnRadiusw.get()

        self.doitWrapper(self.lastNodes,
                         quality = quality,
                         taperLength = taperLength,
                         helixBeaded = helixBeaded,
                         helixWidth = helixWidth,
                         helixThick = helixThick,
                         helixThickness = helixThickness,
                         helixBeadRadius = helixBeadRadius,
                         helixColor1 = self.colors["helixColor1"], # color of helix front faces
                         helixColor2 = self.colors["helixColor2"], # color of helix back faces
                         helixBeadColor1 = self.colors["helixBeadColor1"],
                         helixBeadColor2 = self.colors["helixBeadColor2"],

                         coilRadius = coilRadius,
                         coilColor = self.colors["coilColor"],

                         turnRadius = turnRadius,
                         turnColor = self.colors["turnColor"],

                         sheetBeaded = sheetBeaded,
                         sheetWidth = sheetWidth,
                         sheetBodyStartScale = sheetBodyStartScale,
                         sheetThick = sheetThick,
                         sheetThickness = sheetThickness,
                         sheetBeadRadius = sheetBeadRadius,
                         sheetColor1 = self.colors["sheetColor1"],
                         sheetColor2 = self.colors["sheetColor2"],
                         sheetBeadColor1 = self.colors["sheetBeadColor1"],
                         sheetBeadColor2 = self.colors["sheetBeadColor2"],
                         #sheetColor = (1,0,1)
                         #sheetRgroupSideColor = (1,1,0)
                         #sheetRgroupOppositeSideColor = (1,1,0)
                     #sheetBeadColor = (1,1,1)
                     sheetArrowhead = sheetArrowhead,
                     sheetArrowheadWidth = sheetArrowheadWidth,
                     sheetArrowHeadLength = sheetArrowHeadLength
                     )



    def guiCallback(self):
        self.clearStrandVar()

        selection = self.vf.getSelection()
        if not len(selection): return

        if self.master == None:
            self.master = tkinter.Toplevel()
            self.master.protocol('WM_DELETE_WINDOW', self.hide)
            self.balloon = Pmw.Balloon(self.vf.GUI.ROOT)
            # create NoteBook widget
            self.notebook = notebook = Pmw.NoteBook(self.master)
            notebook.pack(expand='yes', fill='both')

            #
            #GENERAL page
            #
            general = notebook.add("General")
            # add widgets to "General" page:

            # frame containing quality and taper length thumbwheels
            self.frame1 = frame1 = tkinter.Frame(general, bd=2, relief='groove',)
            frame1.pack(expand=1, fill='both', side = 'top')
            
            self.qualityw = qualityw = ThumbWheel(frame1,
                showLabel=1, width=70, height=16, type=int, value=12,
                callback=self.rebuild, continuous=False, oneTurn=10,min=4,
                wheelPad=2, labCfg = {'text':'quality:    ', 'side':'left'})
            qualityw.pack(side='top', anchor='w', padx = 5, pady = 5)
            
            self.taperLengthw = taperLengthw = ThumbWheel(frame1,
                showLabel=1, width=70, height=16, type=int,
                value=qualityw.get()/2, callback=self.rebuild,
                continuous=False, oneTurn=10, min=0,
                wheelPad=2, labCfg = {'text':'taperLength:', 'side':'left'})
            taperLengthw.pack(side='top', anchor='w',padx = 5, pady = 5)

            ## Create radio buttons from PROSS and FILE for molecules
            ## that have SS info in file
            #self.fileProssFrame = f =  Tkinter.Frame(frame1)
            #f.pack(side='top', anchor='w')
            mols = selection.top.uniq()
            self.molModeVars = {}
            self.molFrames = {}
            for mol in mols:
                if mol.parser.hasSsDataInFile():
                    #create radio button if both file and pross are possible
                    self.addFileProssRadioButtons(mol.name)

            #
            # COILS page
            #
            coils = notebook.add("Coils")
            # add widgets to "Coils" page:

            # Coils group
            group = w = Pmw.Group(coils, tag_text='COIL')
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.coilRadiusw = coilRadiusw = ThumbWheel(
                parent, showLabel=1, width=70, height=16, type=float,
                value=0.2,
                callback=self.rebuild, continuous=False, oneTurn=1.,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            coilRadiusw.grid(row=0, column=0, sticky='w')

            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "coilColor", 'Coil Color')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')
            
            # Turn group
            group = w = Pmw.Group(coils, tag_text='TURN')
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.turnRadiusw = turnRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.2,
                callback=self.rebuild, continuous=False, oneTurn=1.,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            turnRadiusw.grid(row=0, column=0, sticky='w')

            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "turnColor", "Turn color")
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')

            #
            # HELIX page
            #
            helix = notebook.add("Helix")
            # add widgets to "Helix" page:
            
            # frame containing width thumbwheel , front/back faces colors
            frame2 = tkinter.Frame(helix)
            frame2.pack(side='top', anchor='nw', fill='both')#, expand=1)
            
            self.helixWidthw = ThumbWheel(frame2,
                showLabel=1, width=70, height=16, type=float, value=1.6,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
                wheelPad=2, labCfg = {'text':'Width:', 'side':'left'})
            self.helixWidthw.grid(row=0, column=0, sticky='nw')
            
            # helix color icons: 
            lab1 = tkinter.Label(frame2, text="Outside:", anchor="w",
                                 justify=tkinter.LEFT)
            lab1.grid(row=0, column=2, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixColor1",
                                  'Helix Outside Color')
            b = tkinter.Button(frame2, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=3, sticky='nw')

            lab2 = tkinter.Label(frame2, text="inside:", anchor="w",
                                 justify=tkinter.LEFT)
            lab2.grid(row=0, column=4, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixColor2",
                                  'Helix Inside Color')
            b = tkinter.Button(frame2, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=5, sticky='nw')
                                  
            # Beads group:
            self.helixBeadedvar = tkinter.IntVar()
            self.helixBeadedvar.set(1)
            self.helixBeadsGroup = w = Pmw.Group(helix, tag_text='Beads',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.helixBeadedvar,
                                  collapsedsize = 2,
                                  tag_command = self.helixBeaded_cb ) 
            parent = w.interior()
            w.pack(fill = 'both', expand = 1, side='left', padx=4, pady=4)
            
            self.helixBeadRadiusw = helixBeadRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.32,
                callback=self.rebuild, continuous=False, oneTurn=.1,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            helixBeadRadiusw.grid(row=0, column=0, sticky='w',columnspan=2)
            
            #lab1 = Tkinter.Label(parent, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixBeadColor1",
                                  'Helix Bead Color1')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=2, sticky='w')

            #lab2 = Tkinter.Label(parent, text="color2:", anchor="w",
            #                     #justify=Tkinter.LEFT)
            #lab2.grid(row=1, column=2, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixBeadColor2",
                                  'Helix Bead Color2')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=3, sticky='w')

            # Thick group
            self.helixThickvar = tkinter.IntVar()
            self.helixThickvar.set(1)
            self.helixThickGroup = w = Pmw.Group(helix, tag_text='Thickness',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.helixThickvar,
                                  tag_command = self.helixThick_cb) #self.rebuild ) 
            parent = w.interior()
            w.pack(fill = 'both', expand = 1, side='left',padx=4, pady=4)
            
            self.helixThicknessw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=.20,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.2,
                wheelPad=2, #labCfg = {'text':'thickness:', 'side':'top'}
                                              )
            self.helixThicknessw.grid(row=0, column=0, sticky='w')
            #            
            # SHEET  page
            #
            sheet = notebook.add("Sheet")
            # add widgets to "Sheet" page
            # frame containing width thumbwheel, BodyStartScale thumbwheel and inside/outside colors: 
            frame3 = tkinter.Frame(sheet)
            frame3.pack(side='top', anchor='nw', fill='both', expand=1)
            
            self.sheetBodyStartScalew = ThumbWheel(frame3,
                showLabel=1, width=70, height=16, type=float, value=.4,
                callback=self.rebuild, continuous=False, oneTurn=1., min=0.1,
                wheelPad=2, labCfg = {'text':'Width: start', 'side':'left'})
            self.sheetBodyStartScalew.grid(row=0, column=0, sticky='nw', columnspan=2)
            self.sheetWidthw = ThumbWheel(frame3,
               showLabel=1, width=70, height=16, type=float, value=1.6,
               callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
               wheelPad=2, labCfg = {'text':'end', 'side':'left'})
            self.sheetWidthw.grid(row=0, column=2, sticky='nw', columnspan=2)

            # sheet color icons: 
            #lab1 = Tkinter.Label(frame3, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "sheetColor1",
                                  'Sheet Color 1')
            b = tkinter.Button(frame3, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=4, sticky='nw')

            #lab2 = Tkinter.Label(frame3, text="back faces:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab2.grid(row=1, column=2, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "sheetColor2",
                                  'Sheet Color 2')
            b = tkinter.Button(frame3, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=5, sticky='nw')
            # frame containing Beads and Thick groups
            frame4 = tkinter.Frame(sheet)
            frame4.pack(side='top', anchor='nw', fill='both', expand=1)
            
            # Beads group:            
            self.sheetBeadedvar = tkinter.IntVar()
            self.sheetBeadedvar.set(1)
            self.sheetBeadGroup = w = Pmw.Group(frame4, tag_text='Beads',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetBeadedvar,
                                  tag_command = self.sheetBeaded_cb)#self.rebuild ) 
            parent = w.interior()
            w.pack(side='left', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.sheetBeadRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.32,
                callback=self.rebuild, continuous=False, oneTurn=0.1,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            self.sheetBeadRadiusw.grid(row=0, column=0, sticky='w')#,
                                       #columnspan=3)
            #lab1 = Tkinter.Label(parent, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor,"sheetBeadColor1",
                                  'Sheet Bead Color 1')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')

            #lab2 = Tkinter.Label(parent, text="color2:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab2.grid(row=2, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor,"sheetBeadColor2",
                                  'Sheet Bead Color 2')                     
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=2, sticky='w')

            # Thick group
            self.sheetThickvar = tkinter.IntVar()
            self.sheetThickvar.set(1)
            self.sheetThickGroup = w = Pmw.Group(frame4, tag_text='Thickness',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetThickvar,
                                  tag_command = self.sheetThick_cb ) 
            parent = w.interior()
            w.pack(side='left', anchor='nw', padx=4, pady=4, fill='both', expand=1 )

            self.sheetThicknessw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=.20,
                callback=self.rebuild, continuous=False, oneTurn=10., min=0.2,
                wheelPad=2, #labCfg = {'text':'Thickness:', 'side':'left'}
                                              )
            self.sheetThicknessw.grid(row=0, column=0, sticky='w')

            #ArrowHead Group:
            self.sheetArrowheadvar = tkinter.IntVar()
            self.sheetArrowheadvar.set(1)
            self.sheetArrowheadGroup = w = Pmw.Group(sheet, tag_text='Arrowhead',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetArrowheadvar,
                                  tag_command = self.sheetArrowhead_cb ) 
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4,fill='both', expand=1 )
            
            self.sheetArrowHeadLengthw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=int, value=8,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=3,
                wheelPad=2, labCfg = {'text':'Length:', 'side':'left'})
            self.sheetArrowHeadLengthw.grid(row=0, column=0, sticky='w')
            
            self.sheetArrowheadWidthw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=2.0,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
                wheelPad=2, labCfg = {'text':'Width:', 'side':'left'})
            self.sheetArrowheadWidthw.grid(row=0, column=1, sticky='w')
            
            #
            #Sheet Edit page
            #
            coils = notebook.add("Strand Edit")
            # add widgets to "flip Sheet Colors" page:

        else:
            self.master.deiconify()
            self.master.lift()

        if selection != self.lastNodes:
            self.doitWrapper(selection)
            self.lastNodes = selection


    def hide(self):
        self.master.withdraw()

    def addFileProssRadioButtons(self, molname):
        f =  tkinter.Frame(self.frame1)
        v = tkinter.StringVar()
        v.set("From File")
        l = tkinter.Label(f, text = "%s: " % molname)
        l.grid(row=0, column=0, sticky='w')
        r1 = tkinter.Radiobutton(f, text="From File", variable=v,
                                 value="From File",# indicatoron=0,
                                 command = self.filePross_cb)
        r1.grid(row=0, column=1, sticky='w')
        self.balloon.bind(r1, "get the information from the file")
        r2 = tkinter.Radiobutton(f, text="From PROSS", variable=v,
                                 value="From Pross", #indicatoron=0,
                                 command = self.filePross_cb)
        r2.grid(row=0, column=2, sticky='w')
        self.balloon.bind(r2, "use PROSS program to calculate sec.structure")
        f.pack(side='top', anchor='w', padx=4, pady=4)
        self.molModeVars[molname] = v
        self.molFrames[molname] = f 


    def setColor(self, objcolor, title):
        from mglutil.gui.BasicWidgets.Tk.colorWidgets import ColorChooser
        def cb(color):
            #print "setColor cb", color
            self.colors[objcolor] = color
            self.rebuild()
        cc = ColorChooser(immediate=1, commands=cb, title=title)
        cc.pack(expand=1, fill='both')

    def filePross_cb(self):
        selection = self.vf.getSelection()
        if not len(selection): return
        if selection != self.lastNodes:
            self.lastNodes = selection
        self.rebuild()


    def helixBeaded_cb(self, event=None):
        """Callback of the Beadss group checkbutton (Helix page) """
        if not self.helixBeadedvar.get():
            self.helixBeadsGroup.collapse()
        else:
            self.helixBeadsGroup.expand()
        self.rebuild()


    def helixThick_cb(self, event=None):
        if not self.helixThickvar.get():
            self.helixThickGroup.collapse()
        else:
            self.helixThickGroup.expand()
        self.rebuild()


    def sheetBeaded_cb(self, event=None):
        if not self.sheetBeadedvar.get():
            self.sheetBeadGroup.collapse()
        else:
            self.sheetBeadGroup.expand()
        self.rebuild()

    def sheetThick_cb(self, event=None):
        if not self.sheetThickvar.get():
            self.sheetThickGroup.collapse()
        else:
            self.sheetThickGroup.expand()
        self.rebuild()

    def sheetArrowhead_cb(self, event=None):
        if not self.sheetArrowheadvar.get():
            self.sheetArrowheadGroup.collapse()
        else:
            self.sheetArrowheadGroup.expand()
        self.rebuild()

        
beadedRibbonsGUI = CommandGUI()
beadedRibbonsGUI.addMenuCommand('menuRoot', 'Compute','Beaded Ribbons')


class BeadedRibbonsUniqCommand(MVCommand):
    """
    Command to compute Beaded Ribbons for selected molecule(s)
    \nPackage : Pmv
    \nModule  : beadedRibbonsCommands
    \nClass   : BeadedRibbonsCommand
    \nCommand name : beadedRibbons
    """

    def __init__(self):
        MVCommand.__init__(self)
        self.master = None
        self.colors = {"helixColor1" :(1,1,1), # color of helix front faces
                       "helixColor2" :(1,0,1), # color of helix back faces
                       "helixBeadColor1" :(1,1,1),
                       "helixBeadColor2" :(1,1,1),
                       "coilColor" :(1,1,1),
                       "turnColor": (0,0,1),
                       "sheetColor1":(1,1,0),
                       "sheetColor2":(0,1,1),
                       "sheetBeadColor1":(1,1,1),
                       "sheetBeadColor2":(1,1,1)}
        self.lastNodes = None
        self.molModeVars = {}
        self.molFrames = {}
        self.strandW = [] # list of checkbuttons for strand color flipping
        self.redo = False

    def setupUndoBefore(self, nodes, **kw):
        for mol in nodes.top.uniq():
            if hasattr(mol, 'beadedRibbonParams'):
                self.addUndoCall( (MoleculeSet([mol]),),
                                  mol.beadedRibbonParams, self.name )


    def onAddCmdToViewer(self):
        self.vf.browseCommands('secondaryStructureCommands',  log=0)


    def onAddObjectToViewer(self, obj):
        #print "onAddObjectToViewer:", obj
        if self.master and self.vf.hasGui:
            if obj in self.vf.Mols:
                self.addFileProssRadioButtons(obj.name)

    def onRemoveObjectFromViewer(self, mol):
        if self.master:
            if mol.name in self.molFrames:
                f = self.molFrames.pop(mol.name)
                f.destroy()
            if mol.name in self.molModeVars:
                self.molModeVars.pop(mol.name)
            self.hide()


    def clearStrandVar(self):
        for w in self.strandW:
            w.destroy()
        self.strandW = []


    def flipStrandColor(self, molName, chainId, SSname):
        vi = self.vf.GUI.VIEWER
        f1 = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
            molName, chainId, SSname+'_faces'))
        f2 = vi.FindObjectByName('root|%s|beadedRibbon|chain%s|%s'%(
            molName, chainId, SSname+'_faces2'))
        from opengltk.OpenGL import GL
        color1 = f1.materials[GL.GL_FRONT].prop[1].copy()
        color2 = f2.materials[GL.GL_FRONT].prop[1].copy()
        f1.Set(materials = color2)
        f2.Set(materials = color1)
        
        
    def __call__(self, nodes, **kw):
        """None<-beadedRibbons(nodes, **kw)
        \nRequired Arguments:\n
            \nnodes  ---  current selection
        \nOptional Arguments:\n
             \nquality --- number of segments per residue (default 12)
             \ntaperLength --- number of points needed to close (taper off) the ribbon (default quality/2)
             \nhelixBeaded --- if set to True - add beads to helix (default True)
             \nhelixCylinder --- if set to True - no beads, helix replace by cylinder (default False)
             \nhelixWidth ---(default 1.6)
             \nhelixThick --- if set to True - add thikness to helix (default True)
             \nhelixThickness --- helix thickness (default.20 )
             \nhelixBeadRadius --- radius of helix beads(default 0.32)
             \nhelixColor1 --- helix outside color(default(1,1,1)
             \nhelixColor2 --- helix inside color (default1,0,1)
             \nhelixBeadColor1 --- color of beads on one side of helix (default (1,1,1))
             \nhelixBeadColor2  --- color of beads on the other side of helix (default (1,1,1) )
             
             \ncoilRadius --- coil radius(default 0.2)
             \ncoilColor --- coil color (default (1,1,1))
             
             \nturnRadius --- turn radius (default 0.2)
             \nturnColor --- turn color (default (0,0,1))
             
             \nsheetBeaded --- (if set to True - add beads to sheet (default True)
             \nsheetWidth --- width of sheet(default 1.6)
             \nsheetBodyStartScale --- (default 0.4)
             \nsheetThick --- if set to True - add thikness to sheet(default True)
             \nsheetThickness --- sheet thickness (default .20)
             \nsheetBeadRadius --- radius of sheet's beads (default 0.32)
             \nsheetColor1 --- sheet outside color (default (1,1,0) )
             \nsheetColor2 --- sheet inside color (default (0,1,1) )
             \nsheetBeadColor1 --- color of beads  on one side of sheet (default (1,1,1) )
             \nsheetBeadColor2 --- color of beads on the other side of beads (default (1,1,1) )
             \nsheetArrowhead --- if set to True - add arrows to sheet(default True)
             \nsheetArrowheadWidth --- width of sheet's arrow (default 2.0)
             \nsheetArrowHeadLength --- length of sheet's arrow (default 8
        """
        nodes = self.vf.expandNodes(nodes)
        if not nodes: return
        self.doitWrapper(nodes, **kw)
        self.lastNodes = nodes


    def extendArray(self,totalv,totalf,totaln,totalcolor,vertices,faces,vnormals,color):
        m = len(totalf)
        m = len(totalv)         
        totalf.extend(numpy.array(faces)+m)
        totalv.extend(vertices)
        totaln.extend(vnormals)
        c = numpy.array([color,]*len(vertices))
        totalcolor.extend(c.tolist())						
        return totalv,totalf,totaln,totalcolor
        
    def doit(self, nodes,
             quality = 12,  # number of segments per residue
             taperLength = None, # default to quality/2
             taperType = "sin", #detault is sinusoidale.
             helixBeaded = True,
             helixCylinder = False,
             helixWidth = 1.6,
             helixThick = True,
             helixThickness = .20,
             helixBeadRadius = 0.32,
             helixColor1 = (1,1,1), # color of helix front faces
             helixColor2 = (1,0,1), # color of helix front faces
             helixBeadColor1 = (1,1,1),
             helixBeadColor2 = (1,1,1),
             helixSideColor = (0,1,0),
             coilRadius = 0.2,
             coilColor = (1,1,1),
             
             turnRadius = 0.2,
             turnColor = (0,0,1),
             
             sheetBeaded = True,
             sheetWidth = 1.6,
             sheetBodyStartScale = 0.4,
             sheetThick = True,
             sheetThickness = .20,
             sheetBeadRadius = 0.32,
             sheetColor1 = (1,1,0),
             sheetColor2 = (0,1,1),
             sheetBeadColor1 = (1,1,1),
             sheetBeadColor2 = (1,1,1),
             sheetSideColor = (0,1,0),
             sheetArrowhead = True,
             sheetArrowheadWidth = 2.0,
             sheetArrowHeadLength = 8):

        # build dict of parameters used to restore in session and undo
        if helixCylinder :
            helixBeaded = False
        params = {
            'quality':quality,
            'taperLength':taperLength,
            'taperType':taperType,
            'helixBeaded':helixBeaded,
            'helixCylinder':helixCylinder,
            'helixWidth':helixWidth,
            'helixThick':helixThick,
            'helixThickness':helixThickness,
            'helixBeadRadius':helixBeadRadius,
            'helixColor1':helixColor1,
            'helixColor2':helixColor2,
            'helixBeadColor1':helixBeadColor1,
            'helixBeadColor2':helixBeadColor2,             
            'helixSideColor':helixSideColor,             
            'coilRadius':coilRadius,
            'coilColor':coilColor,
            'turnRadius':turnRadius,
            'turnColor':turnColor,
            'sheetBeaded':sheetBeaded,
            'sheetWidth':sheetWidth,
            'sheetBodyStartScale':sheetBodyStartScale,
            'sheetThick':sheetThick,
            'sheetThickness':sheetThickness,
            'sheetBeadRadius':sheetBeadRadius,
            'sheetColor1':sheetColor1,
            'sheetColor2':sheetColor2,
            'sheetBeadColor1':sheetBeadColor1,
            'sheetBeadColor2':sheetBeadColor2,
            'sheetSideColor':sheetSideColor,             
            'sheetArrowhead':sheetArrowhead,
            'sheetArrowheadWidth':sheetArrowheadWidth,
            'sheetArrowHeadLength':sheetArrowHeadLength,
        }
        vi = None
        if self.vf.hasGui :
            vi = self.vf.GUI.VIEWER
          
        totalv=[]
        totalf=[] 
        totaln=[]         
        totalcolor=[]
        helixBeadRadius *=.25
        sheetBeadRadius *=.25
        
        pi2 = pi*.5
            
        ## create Circle shapes for beads, Rutns and Coils
        from DejaVu.Shapes import Circle2D
        circleHB = Circle2D( helixBeadRadius )
        circleSB = Circle2D( sheetBeadRadius )
        circleT = Circle2D( turnRadius )
        circleC = Circle2D( coilRadius )

        # these values are ignored
        gapEnd = gapBeg = 2
        frontcap = endcap = 0

        for mol in nodes.top.uniq():
            if not hasattr(self.vf, 'secondarystructureset') or self.redo:
                # FIXME use self.molModVars to use PROSS or file info for SS
                if mol.name not in self.molModeVars:
                    if mol.parser.hasSsDataInFile():
                        mod = "From File"
                    else:
                        mod = "From Pross"
                else:
                    mod = self.molModeVars[mol.name].get()
                print ("recompute",mod)
                self.vf.computeSecondaryStructure(
                    mol, molModes={'%s'%mol.name:mod}, topCommand=0)

            # check mol.strandVar
            createStrandVar = False
            if not hasattr(mol, 'strandVar'):
                mol.strandVar = {}
                createStrandVar = True
            elif len(mol.strandVar) > 0:
                for chain in mol.chains:
                    if createStrandVar is False:
                        for SS in enumerate(chain.secondarystructureset):
                            if SS.__class__.__name__=='Strand':
                                #print SS, mol.strandVar.has_key('%s%s%s'%(mol.name, chain.id,SS.name))
                                if '%s%s%s'%(mol.name, chain.id,SS.name) not in mol.strandVar:
                                    mol.strandVar = {}
                                    createStrandVar = True
                                    break

            mol.beadedRibbonParams = params
            # create a master geometry for the beaded ribbon
            col = row = 0

            for chain in mol.chains:
                chainMaster=self.vf.helper.getObject(mol.name+chain.name+"_beadedRibbon")
                parent = mol.geomContainer.masterGeom.chains_obj[chain.name]
                #not the mastergeom mol.geomContainer.geoms['master'].obj
                if chainMaster is None:
                    chainMaster=self.vf.helper.newEmpty(mol.name+chain.name+"_beadedRibbon")
                    self.vf.helper.addObjectToScene(None,chainMaster,parent=parent)
                # create a master geometry for the beaded ribbon ALREADY CREATE line 263 ?
#                molMaster = Geom('beadedRibbon')
#                if self.vf.hasGui :
#                    vi.AddObject(molMaster, parent=mol.geomContainer.geoms['master'])
#                else :
#                    mol.geomContainer.geoms['master'].children.append(molMaster)
#                    molMaster.parent = mol.geomContainer.geoms['master']
                if not hasattr(chain, 'sheet2D') or \
                   'beadedRibbonSheet' not in chain.sheet2D or self.redo:
                    if chain.ribbonType()=='NA':
                        chain.sheet2D={}
                        ExtrudeNA(chain,name='beadedRibbonSheet')
                    else :
                        self.vf.computeSheet2D(chain, 'beadedRibbonSheet', 'CA', 'O',
                                       buildIsHelix=1, nbrib=2,
                                       nbchords=quality, width=1.0, offset=1.2,
                                       topCommand=0)
                sheet = chain.sheet2D['beadedRibbonSheet']
    
#               # path is at the center of the 2D sheet
                path = sheet.path.copy()
                # n1 is normal to path and in the plane of the 2D sheet
                n1 = sheet.normals
                # b1 is orthogonal to 2D sheet plane
                b1 = sheet.binormals
                # compute Gaussian transport matrices for path 3D
                matrix = sheet.buildTransformationMatrix(path, n1, b1)
    
                # make a copy of the 3D path on each edge of the 2D sheet
                path1 = sheet.smooth[0,:,:3].copy()
                path2 = sheet.smooth[1,:,:3].copy()
                matrix1 = sheet.buildTransformationMatrix(path1, n1, b1)
                matrix2 = sheet.buildTransformationMatrix(path2, n1, b1)
    
                # set variable used to find portions of path 3d and 2D faces
                chords = sheet.chords
                lastResIndex = len(sheet.resInSheet)-1
                sheet.resInSheet.resIndInSheet = list(range(lastResIndex+1))
                lengthPath = len(sheet.path)
    
                # set length of taper in number of points along the path
                if taperLength is None:
                    c2 = int(chords/2)
                else:
                    c2 = int(taperLength)
    
            ##
            ## loop over SS elements and taper path1 and path2 at beginning and end
            ## by moving points in path1 and path2
            ##
                for i, SS in enumerate(chain.secondarystructureset):
                    # get start and end index into path for first residue in SSelement
                    start, end1 = self.getResPts(
                        SS.start.resIndInSheet, chords, lastResIndex, lengthPath)
                    # get start and end index into path for last residue in SSelement
                    start1, end = self.getResPts(
                        SS.end.resIndInSheet, chords, lastResIndex, lengthPath)
    
                    # the first point in path is way off so we ignore it and start
                    # at the CA of the first residue
                    if start == 0: start=1
    
                    sstype = SS.__class__.__name__
                    if chain.ribbonType()=='NA':
                        sstype = 'Helix'
                    ## handle Helices and strand
                    if sstype in ['Strand', 'Helix']:
    
                        # change path1 and path2 to taper begin and end
                        p1 = path1[start:end]
                        p2 = path2[start:end]
                        p = path[start:end]
    
                        ##
                        ## Helix
                        ##
                        if sstype =='Helix':
                            width = helixWidth
                            endSca = 1.0 # this measn no arrow head at the end
                            # tapper begin: first c2 points
                            # 
                            for i in range(c2):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                if taperType == "sin" :
                                    q = sin((i/float(c2))*pi2)*width
                                elif taperType == "cos" :
                                    q = cos(pi2-(i/float(c2))*pi2)*width
                                elif taperType == "linear":
                                    q = (i/float(c2))*width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # scale helix to width
                            length = (len(p)-(2*c2))-1
                            for i in range(c2, c2+length+1):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                q = width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # tapper end: last c2 points
                            for i in range(c2):
                                # tapper end
                                i1 = -i-1
                                x1,y1,z1 = p1[i1]
                                x2,y2,z2 = p2[i1]
                                x,y,z = p[i1]
                                if taperType == "sin" :
                                    q = endSca*sin((i/float(c2))*pi2)*width
                                elif taperType == "cos" :
                                    q = endSca*cos(pi2-(i/float(c2))*pi2)*width
                                elif taperType == "linear":
                                    q = endSca*(i/float(c2))*width
                                #print 'End', i1, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i1] = (p[i1][0] + vx1, p[i1][1]+vy1, p[i1][2]+vz1)
                                p2[i1] = (p[i1][0] + vx2, p[i1][1]+vy2, p[i1][2]+vz2)
    
                        ##
                        ## STRAND
                        ##
                        else:                      
                            width = sheetWidth
                            if sheetArrowhead:
                                endSca = sheetArrowheadWidth
                            else:
                                endSca = 1.0
    
                            # start of sheet is only sheetBodyStartScale% width
                            sca = sheetBodyStartScale
    
                            # tapper begin to sheetBodyStartScale% width
                            for i in range(c2):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                if taperType == "sin" :
                                    q = sin((i/float(c2))*pi2)*sca*width
                                elif taperType == "cos" :
                                    q = cos(pi2-(i/float(c2))*pi2)*sca*width
                                elif taperType == "linear":
                                    q = (i/float(c2))*sca*width
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                #print 'Sheet start', i, q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # scale path from sheetBodyStartScale% to 100% width
                            length = len(p)-c2-sheetArrowHeadLength-1#length = (len(p)-(2*c2))-1
                            #print SS, len(p), c2, length
                            for i in range(c2, c2+length+1):
                                x1,y1,z1 = p1[i]
                                x2,y2,z2 = p2[i]
                                x,y,z = p[i]
                                q = (sca + ((1.0-sca)*(i-c2)/length))*width
                                #print 'Sheet body', i, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i] = (p[i][0] + vx1, p[i][1]+vy1, p[i][2]+vz1)
                                p2[i] = (p[i][0] + vx2, p[i][1]+vy2, p[i][2]+vz2)
    
                            # tapper end from 100% width
                            for i in range(sheetArrowHeadLength):
                                i1 = -i-1
                                x1,y1,z1 = p1[i1]
                                x2,y2,z2 = p2[i1]
                                x,y,z = p[i1]
                                if taperType == "sin" :
                                    q = endSca*sin((i/float(sheetArrowHeadLength))*pi2)*width
                                elif taperType == "cos" :
                                    q = endSca*cos(pi2-(i/float(sheetArrowHeadLength))*pi2)*width
                                elif taperType == "linear":
                                    q = endSca*(i/float(sheetArrowHeadLength))*width
                                #print 'Sheet End', i1, q
                                vx1,vy1,vz1 = (x1-x)*q, (y1-y)*q, (z1-z)*q
                                vx2,vy2,vz2 = (x2-x)*q, (y2-y)*q, (z2-z)*q
                                p1[i1] = (p[i1][0] + vx1, p[i1][1]+vy1, p[i1][2]+vz1)
                                p2[i1] = (p[i1][0] + vx2, p[i1][1]+vy2, p[i1][2]+vz2)
                            #p1[i1-1] = p1[i1]
                            #p2[i1-1] = p2[i1]   
                        # update Gaussian transport matrices for path1 and path2
                        # for this SS element
                        matrix1[start:end] = sheet.buildTransformationMatrix(
                                p1, n1[start:end], b1[start:end])
                        matrix2[start:end] = sheet.buildTransformationMatrix(
                                p2, n1[start:end], b1[start:end])
    
                ##
                ## perform the extrusion using path2, path and path1
                ##
                for nss, SS in enumerate(chain.secondarystructureset):
                    start, end1 = self.getResPts(
                        SS.start.resIndInSheet, chords, lastResIndex, lengthPath)
                    start1, end = self.getResPts(
                        SS.end.resIndInSheet, chords, lastResIndex, lengthPath)
    
                    if start==0: start=1 # skip first point because if it far away
                    p1 = path1[start:end]
                    p2 = path2[start:end]
                    pol2 = pol3 = None
    
                    sstype = SS.__class__.__name__
                    if chain.ribbonType()=='NA':
                        sstype = 'Helix'                    
                    if sstype in ['Strand', 'Helix']:
                        #print SS, start, end
                        if sstype=='Helix': prevRad = helixBeadRadius
                        else:prevRad = sheetBeadRadius
    
                        if (sstype=='Helix' and helixBeaded) or \
                               (sstype=='Strand' and sheetBeaded):
                            if sstype=='Helix':
                                color1 = helixBeadColor1
                                color2 = helixBeadColor2
                                circle = circleHB
                            else:
                                color1 = sheetBeadColor1
                                color2 = sheetBeadColor2
                                circle = circleSB
    
                            extruder1 = ExtrudeObject(p1, matrix1[start:end],
                                                      circle, cap1=1, cap2=1)
                            totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                      extruder1.vertices,extruder1.faces,[],color1)
                            extruder2 = ExtrudeObject(p2, matrix2[start:end],
                                                  circle, cap1=1, cap2=1)
                            totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                      extruder2.vertices,extruder2.faces,[],color2)   
                            #color2
                        polv = path1.tolist()+path2.tolist()
                        polf = sheet.faces2D[start:end-1].tolist()
                        poln = numpy.array(sheet.binormals.tolist()+
                                           sheet.binormals.tolist())
                        if sstype=='Helix' :
#                            totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
#                                                                             polv,polf,[],helixColor1)
                            #color = helixColor1
                            # check face normal to make sure back faces are inside
                            mid = int(start + (end-start)/2)
                            x1,y1,z1 = path[mid]
                            x2,y2,z2 = path[mid+1]
                            dbase = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) + (z2-z1)*(z2-z1)
    
                            x1,y1,z1 = path[mid]+poln[mid]
                            x2,y2,z2 = path[mid+1]+poln[mid+1]
                            dend = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) + (z2-z1)*(z2-z1)
    
                            if dbase>dend:
                               #print 'flip faces for', SS
                               fa = [ [f[3], f[2], f[1], f[0]] for f in polf ]
                               vn = numpy.array([ -v for v in poln ])
                               polf = fa
                            else:
                                vn = poln
    
                            if  helixThick:
                                polv = numpy.array(polv)
                                polv1 = polv + vn*helixThickness*.5
                                polv2 = polv - vn*helixThickness*.5
    
                                polf2 = [ [f[3], f[2], f[1], f[0]] for f in polf ]
                                
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                             polv1,polf,[],helixColor1)
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                             polv2,polf2,[],helixColor2)

                                polv3 = polv1.tolist()+polv2.tolist()
                                l1 = len(polv1)
                                a = int(min(polf[0][0], polf[0][-1]))
                                b = int(max(polf[-1][0], polf[-1][-1]))
                                if dbase>dend:
                                    polf31 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]
                                else:
                                    polf31 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                a = int(min(polf[0][1], polf[0][2]))
                                b = int(max(polf[-1][1], polf[-1][2]))
                                if dbase>dend:
                                    polf32 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                else:
                                    polf32 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]

                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                             polv3,polf31+polf32,[],helixSideColor)    
                            else:
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                                             polv,polf,[],helixColor1)                                        
                        else: # strand
                            if sheetThick:
                                polv = numpy.array(polv)
                                polv1 = polv + poln*sheetThickness*.5
                                polv2 = polv - poln*sheetThickness*.5
    
                                polf2 = [ [f[3], f[2], f[1], f[0]] for f in polf ]
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                 polv1,polf,[],sheetColor1) 
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                 polv2,polf2,[],sheetColor2) 

                                polv3 = polv1.tolist()+polv2.tolist()
                                l1 = len(polv1)
                                a = int(min(polf[0][0], polf[0][-1]))
                                b = int(max(polf[-1][0], polf[-1][-1]))
                                polf31 = [ [i, i+1, i+l1+1, i+l1] for i in range(a,b)]
                                a = int(min(polf[0][1], polf[0][2]))
                                b = int(max(polf[-1][1], polf[-1][2]))
                                polf32 = [ [i, i+l1, i+l1+1, i+1] for i in range(a,b)]

                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                 polv3,polf31+polf32,[],sheetSideColor) 
                            else:
                                totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                 polv,polf,[],sheetColor1) 
                    elif sstype in ['Coil', 'Turn']:
    
                        if sstype =='Coil':
                            color = coilColor
                            circle = circleC
                            radii = [coilRadius]*int(end-start)
                            radius = coilRadius
                        else:
                            color = turnColor
                            circle = circleT
                            radii = [turnRadius]*int(end-start)
                            radius = turnRadius
    
                        # find radius of previous element
                        if SS==chain.secondarystructureset[0]:
                            startRad = radius
                        else:
                            startRad = prevRad
    
                        if SS==chain.secondarystructureset[-1]:
                            endRad = radius
                        else:
                            nextss = chain.secondarystructureset[nss+1]
                            nextsstype = nextss.__class__.__name__
                            if chain.ribbonType()=='NA':
                                nextsstype = 'Helix'                    
                            
                            if nextsstype=='Helix':
                                endRad = helixBeadRadius
                            elif nextsstype=='Strand':
                                endRad = sheetBeadRadius
                            elif nextsstype=='Turn':
                                endRad = turnRadius
                            elif nextsstype=='Coil':
                                endRad = coilRadius

                        deltaRad1 = radius-startRad
                        deltaRad2 = radius-endRad
    
                        for i in range(int(c2)):
                            radii[i] = startRad + deltaRad1*(i/float(c2))
                            radii[-i-1] = endRad + deltaRad2*(i/float(c2))
    
                        extruder = ExtrudeCirclesWithRadii(
                                path[start:end], matrix[start:end],
                                radii, cap1=1, cap2=1)
                        totalv,totalf,totaln,totalcolor=self.extendArray(totalv,totalf,totaln,totalcolor,
                                                 extruder.vertices,extruder.faces,[],color)
                        prevRad = endRad
                chain_bead = self.vf.helper.getObject("b"+mol.name+"_"+chain.name)
                if chain_bead is None :
                    chain_bead = self.vf.helper.createsNmesh("b"+mol.name+"_"+chain.name,
                                        numpy.array(totalv),[],numpy.array(totalf))[0]
                    self.vf.helper.addObjectToScene(None,chain_bead,parent=chainMaster)
                else :
                    self.vf.helper.updateMesh(chain_bead,vertices=numpy.array(totalv),
                                                      faces = numpy.array(totalf))
                #self.vf.helper.changeColor(chain_bead,numpy.array(totalcolor))#,proxyObject=True,perVertex=True)
        setOn = AtomSet([])
        setOff = AtomSet([])        
        if self.createEvents:
            event = EditGeomsEvent(
            'beadU', [nodes,[params,]],
                                    setOn=setOn, setOff=setOff)
            self.vf.dispatchEvent(event)


    def getResPts(self, residueindex, chords, lastResIndex, lengthPath):
        """ return the index of the first and the last point in the
        Sheet2D.path for the residue whose index is specified"""
        # a residue is represented in the path3D by chords points.
        # first residue represented by nbchords/2 + 1
        # last residue represented by nbchords+nbchords/2
        # all other by nbchords.
        if residueindex == 0:
            fromPts = 0
            toPts = chords/2 + 2

        elif residueindex == lastResIndex:
            fromPts = (residueindex-1) * chords + chords/2+1
            toPts = lengthPath-1

        else:
            fromPts = (residueindex-1) * chords + chords/2+1
            toPts = fromPts + chords +1

        toPts = toPts#-self.gapEnd
        fromPts = fromPts# + self.gapBeg
        return fromPts,toPts


    def rebuild(self, event=None):
        quality = self.qualityw.get()
        taperLength = self.taperLengthw.get()

        helixBeaded = self.helixBeadedvar.get()
        helixWidth = self.helixWidthw.get()
        helixBeadRadius = self.helixBeadRadiusw.get()
        helixThick = self.helixThickvar.get()
        helixThickness = self.helixThicknessw.get()

        sheetBeaded = self.sheetBeadedvar.get()
        sheetThick = self.sheetThickvar.get()
        sheetThickness = self.sheetThicknessw.get()
        sheetWidth = self.sheetWidthw.get()
        sheetBodyStartScale = self.sheetBodyStartScalew.get()
        sheetBeadRadius = self.sheetBeadRadiusw.get()
        sheetArrowhead = self.sheetArrowheadvar.get()
        sheetArrowheadWidth = self.sheetArrowheadWidthw.get()
        sheetArrowHeadLength = self.sheetArrowHeadLengthw.get()

        coilRadius = self.coilRadiusw.get()
        turnRadius = self.turnRadiusw.get()

        self.doitWrapper(self.lastNodes,
                         quality = quality,
                         taperLength = taperLength,
                         helixBeaded = helixBeaded,
                         helixWidth = helixWidth,
                         helixThick = helixThick,
                         helixThickness = helixThickness,
                         helixBeadRadius = helixBeadRadius,
                         helixColor1 = self.colors["helixColor1"], # color of helix front faces
                         helixColor2 = self.colors["helixColor2"], # color of helix back faces
                         helixBeadColor1 = self.colors["helixBeadColor1"],
                         helixBeadColor2 = self.colors["helixBeadColor2"],

                         coilRadius = coilRadius,
                         coilColor = self.colors["coilColor"],

                         turnRadius = turnRadius,
                         turnColor = self.colors["turnColor"],

                         sheetBeaded = sheetBeaded,
                         sheetWidth = sheetWidth,
                         sheetBodyStartScale = sheetBodyStartScale,
                         sheetThick = sheetThick,
                         sheetThickness = sheetThickness,
                         sheetBeadRadius = sheetBeadRadius,
                         sheetColor1 = self.colors["sheetColor1"],
                         sheetColor2 = self.colors["sheetColor2"],
                         sheetBeadColor1 = self.colors["sheetBeadColor1"],
                         sheetBeadColor2 = self.colors["sheetBeadColor2"],
                         #sheetColor = (1,0,1)
                         #sheetRgroupSideColor = (1,1,0)
                         #sheetRgroupOppositeSideColor = (1,1,0)
                     #sheetBeadColor = (1,1,1)
                     sheetArrowhead = sheetArrowhead,
                     sheetArrowheadWidth = sheetArrowheadWidth,
                     sheetArrowHeadLength = sheetArrowHeadLength
                     )



    def guiCallback(self):
        self.clearStrandVar()

        selection = self.vf.getSelection()
        if not len(selection): return

        if self.master == None:
            self.master = tkinter.Toplevel()
            self.master.protocol('WM_DELETE_WINDOW', self.hide)
            self.balloon = Pmw.Balloon(self.vf.GUI.ROOT)
            # create NoteBook widget
            self.notebook = notebook = Pmw.NoteBook(self.master)
            notebook.pack(expand='yes', fill='both')

            #
            #GENERAL page
            #
            general = notebook.add("General")
            # add widgets to "General" page:

            # frame containing quality and taper length thumbwheels
            self.frame1 = frame1 = tkinter.Frame(general, bd=2, relief='groove',)
            frame1.pack(expand=1, fill='both', side = 'top')
            
            self.qualityw = qualityw = ThumbWheel(frame1,
                showLabel=1, width=70, height=16, type=int, value=12,
                callback=self.rebuild, continuous=False, oneTurn=10,min=4,
                wheelPad=2, labCfg = {'text':'quality:    ', 'side':'left'})
            qualityw.pack(side='top', anchor='w', padx = 5, pady = 5)
            
            self.taperLengthw = taperLengthw = ThumbWheel(frame1,
                showLabel=1, width=70, height=16, type=int,
                value=qualityw.get()/2, callback=self.rebuild,
                continuous=False, oneTurn=10, min=0,
                wheelPad=2, labCfg = {'text':'taperLength:', 'side':'left'})
            taperLengthw.pack(side='top', anchor='w',padx = 5, pady = 5)

            ## Create radio buttons from PROSS and FILE for molecules
            ## that have SS info in file
            #self.fileProssFrame = f =  Tkinter.Frame(frame1)
            #f.pack(side='top', anchor='w')
            mols = selection.top.uniq()
            self.molModeVars = {}
            self.molFrames = {}
            for mol in mols:
                if mol.parser.hasSsDataInFile():
                    #create radio button if both file and pross are possible
                    self.addFileProssRadioButtons(mol.name)

            #
            # COILS page
            #
            coils = notebook.add("Coils")
            # add widgets to "Coils" page:

            # Coils group
            group = w = Pmw.Group(coils, tag_text='COIL')
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.coilRadiusw = coilRadiusw = ThumbWheel(
                parent, showLabel=1, width=70, height=16, type=float,
                value=0.2,
                callback=self.rebuild, continuous=False, oneTurn=1.,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            coilRadiusw.grid(row=0, column=0, sticky='w')

            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "coilColor", 'Coil Color')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')
            
            # Turn group
            group = w = Pmw.Group(coils, tag_text='TURN')
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.turnRadiusw = turnRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.2,
                callback=self.rebuild, continuous=False, oneTurn=1.,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            turnRadiusw.grid(row=0, column=0, sticky='w')

            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "turnColor", "Turn color")
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')

            #
            # HELIX page
            #
            helix = notebook.add("Helix")
            # add widgets to "Helix" page:
            
            # frame containing width thumbwheel , front/back faces colors
            frame2 = tkinter.Frame(helix)
            frame2.pack(side='top', anchor='nw', fill='both')#, expand=1)
            
            self.helixWidthw = ThumbWheel(frame2,
                showLabel=1, width=70, height=16, type=float, value=1.6,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
                wheelPad=2, labCfg = {'text':'Width:', 'side':'left'})
            self.helixWidthw.grid(row=0, column=0, sticky='nw')
            
            # helix color icons: 
            lab1 = tkinter.Label(frame2, text="Outside:", anchor="w",
                                 justify=tkinter.LEFT)
            lab1.grid(row=0, column=2, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixColor1",
                                  'Helix Outside Color')
            b = tkinter.Button(frame2, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=3, sticky='nw')

            lab2 = tkinter.Label(frame2, text="inside:", anchor="w",
                                 justify=tkinter.LEFT)
            lab2.grid(row=0, column=4, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixColor2",
                                  'Helix Inside Color')
            b = tkinter.Button(frame2, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=5, sticky='nw')
                                  
            # Beads group:
            self.helixBeadedvar = tkinter.IntVar()
            self.helixBeadedvar.set(1)
            self.helixBeadsGroup = w = Pmw.Group(helix, tag_text='Beads',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.helixBeadedvar,
                                  collapsedsize = 2,
                                  tag_command = self.helixBeaded_cb ) 
            parent = w.interior()
            w.pack(fill = 'both', expand = 1, side='left', padx=4, pady=4)
            
            self.helixBeadRadiusw = helixBeadRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.32,
                callback=self.rebuild, continuous=False, oneTurn=.1,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            helixBeadRadiusw.grid(row=0, column=0, sticky='w',columnspan=2)
            
            #lab1 = Tkinter.Label(parent, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixBeadColor1",
                                  'Helix Bead Color1')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=2, sticky='w')

            #lab2 = Tkinter.Label(parent, text="color2:", anchor="w",
            #                     #justify=Tkinter.LEFT)
            #lab2.grid(row=1, column=2, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "helixBeadColor2",
                                  'Helix Bead Color2')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=3, sticky='w')

            # Thick group
            self.helixThickvar = tkinter.IntVar()
            self.helixThickvar.set(1)
            self.helixThickGroup = w = Pmw.Group(helix, tag_text='Thickness',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.helixThickvar,
                                  tag_command = self.helixThick_cb) #self.rebuild ) 
            parent = w.interior()
            w.pack(fill = 'both', expand = 1, side='left',padx=4, pady=4)
            
            self.helixThicknessw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=.20,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.2,
                wheelPad=2, #labCfg = {'text':'thickness:', 'side':'top'}
                                              )
            self.helixThicknessw.grid(row=0, column=0, sticky='w')
            #            
            # SHEET  page
            #
            sheet = notebook.add("Sheet")
            # add widgets to "Sheet" page
            # frame containing width thumbwheel, BodyStartScale thumbwheel and inside/outside colors: 
            frame3 = tkinter.Frame(sheet)
            frame3.pack(side='top', anchor='nw', fill='both', expand=1)
            
            self.sheetBodyStartScalew = ThumbWheel(frame3,
                showLabel=1, width=70, height=16, type=float, value=.4,
                callback=self.rebuild, continuous=False, oneTurn=1., min=0.1,
                wheelPad=2, labCfg = {'text':'Width: start', 'side':'left'})
            self.sheetBodyStartScalew.grid(row=0, column=0, sticky='nw', columnspan=2)
            self.sheetWidthw = ThumbWheel(frame3,
               showLabel=1, width=70, height=16, type=float, value=1.6,
               callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
               wheelPad=2, labCfg = {'text':'end', 'side':'left'})
            self.sheetWidthw.grid(row=0, column=2, sticky='nw', columnspan=2)

            # sheet color icons: 
            #lab1 = Tkinter.Label(frame3, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "sheetColor1",
                                  'Sheet Color 1')
            b = tkinter.Button(frame3, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=4, sticky='nw')

            #lab2 = Tkinter.Label(frame3, text="back faces:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab2.grid(row=1, column=2, sticky='nw')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor, "sheetColor2",
                                  'Sheet Color 2')
            b = tkinter.Button(frame3, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=5, sticky='nw')
            # frame containing Beads and Thick groups
            frame4 = tkinter.Frame(sheet)
            frame4.pack(side='top', anchor='nw', fill='both', expand=1)
            
            # Beads group:            
            self.sheetBeadedvar = tkinter.IntVar()
            self.sheetBeadedvar.set(1)
            self.sheetBeadGroup = w = Pmw.Group(frame4, tag_text='Beads',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetBeadedvar,
                                  tag_command = self.sheetBeaded_cb)#self.rebuild ) 
            parent = w.interior()
            w.pack(side='left', anchor='nw', padx=4, pady=4, fill='both', expand=1)
            
            self.sheetBeadRadiusw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=0.32,
                callback=self.rebuild, continuous=False, oneTurn=0.1,min=0.001,
                wheelPad=2, labCfg = {'text':'radius:', 'side':'left'})
            self.sheetBeadRadiusw.grid(row=0, column=0, sticky='w')#,
                                       #columnspan=3)
            #lab1 = Tkinter.Label(parent, text="colors:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab1.grid(row=1, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor,"sheetBeadColor1",
                                  'Sheet Bead Color 1')
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=1, sticky='w')

            #lab2 = Tkinter.Label(parent, text="color2:", anchor="w",
            #                     justify=Tkinter.LEFT)
            #lab2.grid(row=2, column=0, sticky='w')
            photo = ImageTk.PhotoImage(
                file=os.path.join(ICONPATH, 'colorChooser20.png'))
            cb = CallbackFunction(self.setColor,"sheetBeadColor2",
                                  'Sheet Bead Color 2')                     
            b = tkinter.Button(parent, command=cb, image=photo)
            b.photo = photo
            b.grid(row=0, column=2, sticky='w')

            # Thick group
            self.sheetThickvar = tkinter.IntVar()
            self.sheetThickvar.set(1)
            self.sheetThickGroup = w = Pmw.Group(frame4, tag_text='Thickness',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetThickvar,
                                  tag_command = self.sheetThick_cb ) 
            parent = w.interior()
            w.pack(side='left', anchor='nw', padx=4, pady=4, fill='both', expand=1 )

            self.sheetThicknessw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=.20,
                callback=self.rebuild, continuous=False, oneTurn=10., min=0.2,
                wheelPad=2, #labCfg = {'text':'Thickness:', 'side':'left'}
                                              )
            self.sheetThicknessw.grid(row=0, column=0, sticky='w')

            #ArrowHead Group:
            self.sheetArrowheadvar = tkinter.IntVar()
            self.sheetArrowheadvar.set(1)
            self.sheetArrowheadGroup = w = Pmw.Group(sheet, tag_text='Arrowhead',
                                  tag_pyclass = tkinter.Checkbutton,
                                  tag_variable = self.sheetArrowheadvar,
                                  tag_command = self.sheetArrowhead_cb ) 
            parent = w.interior()
            w.pack(side='top', anchor='nw', padx=4, pady=4,fill='both', expand=1 )
            
            self.sheetArrowHeadLengthw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=int, value=8,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=3,
                wheelPad=2, labCfg = {'text':'Length:', 'side':'left'})
            self.sheetArrowHeadLengthw.grid(row=0, column=0, sticky='w')
            
            self.sheetArrowheadWidthw = ThumbWheel(parent,
                showLabel=1, width=70, height=16, type=float, value=2.0,
                callback=self.rebuild, continuous=False, oneTurn=10.,min=0.1,
                wheelPad=2, labCfg = {'text':'Width:', 'side':'left'})
            self.sheetArrowheadWidthw.grid(row=0, column=1, sticky='w')
            
            #
            #Sheet Edit page
            #
            coils = notebook.add("Strand Edit")
            # add widgets to "flip Sheet Colors" page:

        else:
            self.master.deiconify()
            self.master.lift()

        if selection != self.lastNodes:
            self.doitWrapper(selection)
            self.lastNodes = selection


    def hide(self):
        self.master.withdraw()

    def addFileProssRadioButtons(self, molname):
        f =  tkinter.Frame(self.frame1)
        v = tkinter.StringVar()
        v.set("From File")
        l = tkinter.Label(f, text = "%s: " % molname)
        l.grid(row=0, column=0, sticky='w')
        r1 = tkinter.Radiobutton(f, text="From File", variable=v,
                                 value="From File",# indicatoron=0,
                                 command = self.filePross_cb)
        r1.grid(row=0, column=1, sticky='w')
        self.balloon.bind(r1, "get the information from the file")
        r2 = tkinter.Radiobutton(f, text="From PROSS", variable=v,
                                 value="From Pross", #indicatoron=0,
                                 command = self.filePross_cb)
        r2.grid(row=0, column=2, sticky='w')
        self.balloon.bind(r2, "use PROSS program to calculate sec.structure")
        f.pack(side='top', anchor='w', padx=4, pady=4)
        self.molModeVars[molname] = v
        self.molFrames[molname] = f 


    def setColor(self, objcolor, title):
        from mglutil.gui.BasicWidgets.Tk.colorWidgets import ColorChooser
        def cb(color):
            #print "setColor cb", color
            self.colors[objcolor] = color
            self.rebuild()
        cc = ColorChooser(immediate=1, commands=cb, title=title)
        cc.pack(expand=1, fill='both')

    def filePross_cb(self):
        selection = self.vf.getSelection()
        if not len(selection): return
        if selection != self.lastNodes:
            self.lastNodes = selection
        self.rebuild()


    def helixBeaded_cb(self, event=None):
        """Callback of the Beadss group checkbutton (Helix page) """
        if not self.helixBeadedvar.get():
            self.helixBeadsGroup.collapse()
        else:
            self.helixBeadsGroup.expand()
        self.rebuild()


    def helixThick_cb(self, event=None):
        if not self.helixThickvar.get():
            self.helixThickGroup.collapse()
        else:
            self.helixThickGroup.expand()
        self.rebuild()


    def sheetBeaded_cb(self, event=None):
        if not self.sheetBeadedvar.get():
            self.sheetBeadGroup.collapse()
        else:
            self.sheetBeadGroup.expand()
        self.rebuild()

    def sheetThick_cb(self, event=None):
        if not self.sheetThickvar.get():
            self.sheetThickGroup.collapse()
        else:
            self.sheetThickGroup.expand()
        self.rebuild()

    def sheetArrowhead_cb(self, event=None):
        if not self.sheetArrowheadvar.get():
            self.sheetArrowheadGroup.collapse()
        else:
            self.sheetArrowheadGroup.expand()
        self.rebuild()

        
beadedRibbonsUniqGUI = CommandGUI()
beadedRibbonsUniqGUI.addMenuCommand('menuRoot', 'Compute','Beaded Ribbons Uniq')



class DisplayBeadedRibbonsCommand(DisplayCommand):
    """Command to display/undisplay beaded ribbons geometries.
    Command operates at the molecule level. To execute this command use
    'Display Beaded Ribbons' entry under the 'Display' menu in the menu bar.
    \nPackage : Pmv
    \nModule  : beadedRibbonsCommands
    \nClass   : displayBeadedRibbonsCommand
    \nCommand name : displayBeadedRibbons
    \nSynopsis:\n
         None <--- displayBeadedRibbons(nodes, **kw)
    \nRequired Arguments:\n    
         nodes --- TreeNodeSet holding the current selection"""



    def onAddCmdToViewer(self):
        self.vf.browseCommands("secondaryStructureCommands", package="Pmv", topCommand = 0)


    #def setupUndoBefore(self, nodes, only=False, negate=False, **kw):
    #    pass


    def doit(self, nodes, only=False, negate=False,**kw ):
        """ displays beaded ribbons for selected molecules"""

        #print "display beaded ribbons: only=", only, " and negate=", negate
        
        mols = nodes.top.uniq() # selected molecules
        vi = None
        if self.vf.hasGui:
            vi = self.vf.GUI.VIEWER
        if negate:
            # undisplay (set visible to False) ribbons of selected molecules
            for mol in mols:
                if hasattr(mol, "beadedRibbonParams"):
                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon'%(
                                        mol.name))
                    #obj =  vi.FindObjectByName('root|%s|beadedRibbon' % mol.name)
                    if obj:
                        self.setVisible(obj, False)
        elif only:
            # display beaded ribbons for the selected molecules only:
            #  - compute ribbon for selected molecules (if it has not benn computed yet)
            #  - set visible to True for existing ribbons of selected molecules
            #  - set visible to False to the existing ribbon for the molecules that are not selected
            
            for mol in self.vf.Mols:
                if mol in mols:
                    if not hasattr(mol, "beadedRibbonParams"):
                        self.vf.beadedRibbons(mol, topCommand=0, log=0)
                    else:
                        obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon'%(
                                        mol.name))
                        #obj =  vi.FindObjectByName('root|%s|beadedRibbon' % mol.name)
                        if obj:
                            self.setVisible(obj, True)
                else:
                    if hasattr(mol, "beadedRibbonParams"):
                        obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon'%(
                                        mol.name))
                        #obj =  vi.FindObjectByName('root|%s|beadedRibbon' % mol.name)
                        if obj:
                            self.setVisible(obj, False)
        
        else: #display (compute) ribbons of selected molecules
            for mol in mols:
                if not hasattr(mol, "beadedRibbonParams"):
                    self.vf.beadedRibbons(mol, topCommand=0, log=0)
                else:
                    obj = self.vf.FindObjectByName_noGui(mol.geomContainer.geoms['master'],'%s|beadedRibbon'%(
                                        mol.name))
#                    obj =  vi.FindObjectByName('root|%s|beadedRibbon' % mol.name)
                    if obj:
                        self.setVisible(obj, True)

        #redraw = False
        #if kw.has_key("redraw") : redraw=True
        #event = EditGeomsEvent('BeadedRibbonsDisplay', [nodes,[only, negate,redraw]],
        #                       setOn=setOn, setOff=setOff)
        #self.vf.dispatchEvent(event)
        

    def __call__(self, nodes, only=False, negate=False,**kw):
        """None <- displayBeadedRibbons(nodes, only=False, negate=False,**kw)
        \nRequired Arguments:\n
            \nnodes  ---  current selection
        \nOptional Arguments:\n
            \nonly ---  flag when set to 1 only the ribbon corresponding to currently selected molecule will be displayed
            \nnegate ---  flag when set to 1 the ribbon corresponding to currently selected molecule will be undisplayed """
        if type(nodes) is StringType:
            self.nodeLogString = "'"+nodes+"'"
        nodes = self.vf.expandNodes(nodes)
        if not nodes: return
        #if not kw.has_key('redraw'):kw['redraw']=1
        kw['only'] = only
        kw['negate'] = negate

        self.clearStrandVar()
        self.doitWrapper(*(nodes,), **kw)

    def setVisible(self, obj, value):
        obj.Set( visible = value)
        if value: # set all parents visibility to 1
            while obj.parent:
                obj = obj.parent
                obj.Set( visible=value )



class UndisplayBeadedRibbonsCommand(DisplayCommand):
    """ UndisplayBeadedRibbonsCommand is an interactive command to undisplay
    computed Beaded Ribbon for selected molecule(s).
    \nPackage : Pmv
    \nModule  : beadedRibbonsCommands
    \nClass   : UndisplayBeadedRibbonsCommand
    \nCommand name : undisplayBeadedRibbons
    \nSynopsis:\n
         None <--- undisplayBeadedRibbons(nodes, **kw)
    \nRequired Arguments:\n    
         nodes --- TreeNodeSet holding the current selection
    """
    
    def onAddCmdToViewer(self):
        if 'displayBeadedRibbons' not in self.vf.commands:
            self.vf.loadCommand('beadedRibbonsCommands',
                                ['displayBeadedRibbons'], 'Pmv',
                                topCommand=0)

        
    def __call__(self, nodes, **kw):
        """None <--- undisplayBeadedRibbons(nodes, **k)
        \nnodes --- TreeNodeSet holding the current selection
        """
        if type(nodes) is StringType:
            self.nodeLogString = "'"+nodes+"'"
        nodes = self.vf.expandNodes(nodes)
        if not nodes: return
        kw['negate']= 1
        self.vf.displayBeadedRibbons(*(nodes,), **kw)


displayBeadedRibbonsGuiDescr = {'widgetType':'Menu', 'menuBarName':'menuRoot',
                                'menuButtonName':'Display',
                                'menuEntryLabel':'Beaded Ribbons'}

displayBeadedRibbonsGUI = CommandGUI()
displayBeadedRibbonsGUI.addMenuCommand('menuRoot', 'Display',
                            'Beaded Ribbons')        
    

commandList  = [{'name':'beadedRibbons','cmd':BeadedRibbonsRegCommand(),'gui':beadedRibbonsGUI},
                 {'name':'beadedRibbonsUniq','cmd':BeadedRibbonsUniqCommand(),'gui':beadedRibbonsUniqGUI},
                {'name':'displayBeadedRibbons','cmd':DisplayBeadedRibbonsCommand(),
                 'gui':displayBeadedRibbonsGUI},
                {'name':'undisplayBeadedRibbons','cmd':UndisplayBeadedRibbonsCommand(),
                 'gui':None},
                ]


def initModule(viewer):
    for _dict in commandList:
        viewer.addCommand(_dict['cmd'],_dict['name'],_dict['gui'])

    
