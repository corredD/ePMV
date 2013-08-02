## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 


############################################################################
#
# Author: Ruth HUEY
#
# Copyright: M. Sanner TSRI 2000
#
#############################################################################

# $Header
#
# $Id: strutsCommands.py,v 1.93.4.1 2010/12/30 21:54:49 rhuey Exp $
#


from ViewerFramework.VFCommand import CommandGUI
from Pmv.moleculeViewer import AddAtomsEvent
from mglutil.gui.BasicWidgets.Tk.colorWidgets import ColorChooser

from mglutil.gui.InputForm.Tk.gui import InputFormDescr
from mglutil.util.callback import CallBackFunction
from mglutil.gui.BasicWidgets.Tk.customizedWidgets \
    import ExtendedSliderWidget, ListChooser
from mglutil.gui.BasicWidgets.Tk.thumbwheel import ThumbWheel
from mglutil.util.misc import ensureFontCase

from Pmv.mvCommand import MVCommand, MVAtomICOM, MVBondICOM
from Pmv.measureCommands import MeasureAtomCommand

from MolKit.molecule import Atom, AtomSet, Bond
from MolKit.molecule import BondSet, HydrogenBond, HydrogenBondSet
from MolKit.distanceSelector import DistanceSelector
from MolKit.strutsBondBuilder import StrutsBondBuilder
from MolKit.pdbWriter import PdbWriter

from DejaVu.Geom import Geom
from DejaVu.Spheres import Spheres
from DejaVu.Points import CrossSet
from DejaVu.Cylinders import Cylinders
from DejaVu.spline import DialASpline, SplineObject
from DejaVu.GleObjects import GleExtrude, GleObject
from DejaVu.Shapes import Shape2D, Triangle2D, Circle2D, Rectangle2D,\
     Square2D, Ellipse2D

from Pmv.stringSelectorGUI import StringSelectorGUI
from PyBabel.util import vec3

import Tkinter, numpy.oldnumeric as Numeric, math, string, os
from string import strip, split
from types import StringType

from opengltk.OpenGL import GL

from DejaVu.glfLabels import GlfLabels

from Pmv.moleculeViewer import DeleteAtomsEvent, AddAtomsEvent, EditAtomsEvent, ShowMoleculesEvent
from Pmv.moleculeViewer import DeleteGeomsEvent, AddGeomsEvent, EditGeomsEvent

#struts geom should be shild of mol.geomContainer.masterGeom
def check_hbond_geoms(VFGUI):
    hbond_geoms_list = VFGUI.VIEWER.findGeomsByName('struts_geoms')
    if hbond_geoms_list==[]:
        hbond_geoms = Geom("struts_geoms", shape=(0,0), protected=True)
        VFGUI.VIEWER.AddObject(hbond_geoms, parent=VFGUI.miscGeom)
        hbond_geoms_list = [hbond_geoms]
    return hbond_geoms_list[0]
 
# lists of babel_types for donor-acceptor 
#   derived from MacDonald + Thornton 
#   'Atlas of Side-Chain + Main-Chain Hydrogen Bonding'
# plus sp2Acceptor Nam


def dist(c1, c2):
    d = Numeric.array(c2) - Numeric.array(c1) 
    ans = math.sqrt(Numeric.sum(d*d))
    return round(ans, 3)

def getAngle(ac, hat, don ):
    acCoords = getTransformedCoords(ac)
    hCoords = getTransformedCoords(hat)
    dCoords = getTransformedCoords(don)
    pt1 = Numeric.array(acCoords, 'f')
    pt2 = Numeric.array(hCoords, 'f')
    pt3 = Numeric.array(dCoords, 'f')
    #pt1 = Numeric.array(ac.coords, 'f')
    #pt2 = Numeric.array(hat.coords, 'f')
    #pt3 = Numeric.array(don.coords, 'f')
    v1 = Numeric.array(pt1 - pt2)
    v2 = Numeric.array(pt3 - pt2)
    dist1 = math.sqrt(Numeric.sum(v1*v1))
    dist2 = math.sqrt(Numeric.sum(v2*v2))
    sca = Numeric.dot(v1, v2)/(dist1*dist2)
    if sca>1.0:
        sca = 1.0
    elif sca<-1.0:
        sca = -1.0
    ang =  math.acos(sca)*180./math.pi
    return round(ang, 5)


def applyTransformation(pt, mat):
    pth = [pt[0], pt[1], pt[2], 1.0]
    return Numeric.dot(mat, pth)[:3]

def getTransformedCoords(atom):
    # when there is no viewer, the geomContainer is None
    if atom.top.geomContainer is None:
        return atom.coords
    g = atom.top.geomContainer.geoms['master']
    c = applyTransformation(atom.coords, g.GetMatrix(g))
    return  c.astype('f')


class BuildStrutsBondsGUICommand(MVCommand):
    """This class provides Graphical User Interface to Struts which is invoked by it.
    \nPackage : Pmv
   \nModule  : hbondCommands
   \nClass   : BuildStrutsBondsGUICommand
   \nCommand : buildStrutsBondsGC
   \nSynopsis:\n
        None<---buildStrutsBondsGC(nodes1, nodes2, paramDict, reset=1)
    """
    

    def onAddCmdToViewer(self):
        if self.vf.hasGui:
            self.showSel = Tkinter.IntVar()
            self.resetVar = Tkinter.IntVar()
            self.resetVar.set(1)
            self.showDef = Tkinter.IntVar()
            self.distOnly = Tkinter.IntVar()
            self.dist = Tkinter.IntVar()
            self.thresh = Tkinter.DoubleVar()
            self.hideDTypeSel = Tkinter.IntVar()
            self.hideATypeSel = Tkinter.IntVar()
            self.showTypes = Tkinter.IntVar()
            varNames = ['hideDSel',  'N3', 'O3','S3','Nam', 'Ng', 'Npl',\
                    'hideASel',  'aS3', 'aO3', 'aO2', 'aO', 'aNpl',
                    'aNam']
            for n in varNames:
                exec('self.'+n+'=Tkinter.IntVar()')
                exec('self.'+n+'.set(1)')



    def doit(self, nodes, paramDict, reset=1):
        #buildHbondGC
        self.hasAngles = 0
        #self.warningMsg('will try to build struts..')
        vStruts = self.vf.buildStruts(nodes, paramDict, reset)
        if not len(vStruts):
            self.warningMsg('no struts bonds found')
            return 'ERROR'
        else:
            msg = str(len(vStruts))+' struts bonds build'
            self.warningMsg(msg)
        self.vf.strutsAsCylinders(nodes)
            
    def guiCallback(self):
        if not len(self.vf.Mols):
            self.warningMsg('no molecules in viewer')
            return 
        if not hasattr(self, 'ifd'):
            self.buildForm()
        else:
            self.form.deiconify()


    def buildForm(self):
        ifd = self.ifd = InputFormDescr(title = "Select nodes + change parameters(optional):")
        ifd.append({'name':'keyLab',
                    'widgetType':Tkinter.Label,
                    'text':'For Struts Bond detection:',
                    'gridcfg':{'sticky':'w'}})
        
        ifd.append({'name': 'molSet',
            'wtype':StringSelectorGUI,
            'widgetType':StringSelectorGUI,
            'wcfg':{ 'molSet': self.vf.Mols,
                    'vf': self.vf,
                    'all':1,
                    'crColor':(0.,1.,.2),
            },
            'gridcfg':{'sticky':'we', 'columnspan':2 }})
        
        ifd.append({'name':'distCutoff',
                    'widgetType':ExtendedSliderWidget,
                    'wcfg':{'label': 'Residue Spacing Minimum',
                            'minval':1,'maxval':50 ,
                            'init':6,
                            'labelsCursorFormat':'%1d',
                            'sliderType':'int',
                            'entrywcfg':{'width':4},
                            'entrypackcfg':{'side':'right'}},
                     'gridcfg':{'columnspan':2,'sticky':'we'}})
        ifd.append({'name':'distCutoff2',
                    'widgetType':ExtendedSliderWidget,
                    'wcfg':{'label': 'Threshold',
                            'minval':1.0,'maxval':50.0 ,
                            'init':5.00,
                            'labelsCursorFormat':'%1.2f',
                            'sliderType':'float',
                            'entrywcfg':{'width':4},
                            'entrypackcfg':{'side':'right'}},
                     'gridcfg':{'columnspan':2,'sticky':'we'}})
        ifd.append({'widgetType': Tkinter.Button,
            'text':'Ok',
            'wcfg':{'bd':6},
            'gridcfg':{'sticky':Tkinter.E+Tkinter.W},
            'command':self.Accept_cb})
        self.form = self.vf.getUserInput(self.ifd, modal=0, blocking=0)
        self.form.root.protocol('WM_DELETE_WINDOW',self.Close_cb)
        self.form.autoSize()

    def cleanUpCrossSet(self):
        chL = []
        for item in self.vf.GUI.VIEWER.rootObject.children:
            if isinstance(item, CrossSet) and item.name[:8]=='strSelCr':
                chL.append(item)
        if len(chL):
            for item in chL: 
                item.Set(vertices=[], tagModified=False)
                self.vf.GUI.VIEWER.Redraw()
                self.vf.GUI.VIEWER.RemoveObject(item)


    def Close_cb(self, event=None):
        #self.cleanUpCrossSet()
        self.form.withdraw()
        #self.form.destroy(
    
    def Accept_cb(self, event=None):
        self.form.withdraw()
        node = self.ifd.entryByName['molSet']['widget'].get()
        if node is None :
            node = self.vf.getSelection()
            #nodesToCheck2 = self.vf.getSelection()
        if not len(node):
            self.warningMsg('no atoms in first set')
            return
        dist = self.ifd.entryByName['distCutoff']['widget'].get()
        thresh = self.ifd.entryByName['distCutoff2']['widget'].get()

        if node[0].__class__!=Atom:
            ats1 = node.findType(Atom)
            node = ats1
        self.Close_cb()
        paramDict = {}
        paramDict['distCutoff'] = dist
        paramDict['distCutoff2'] = thresh
        #print 'donorList=', donorList
        #print 'acceptorList=', acceptorList
        return self.doitWrapper(node, 
            paramDict, reset=self.resetVar.get(), topCommand=0)



BuildStrutsBondsGUICommandGuiDescr = {'widgetType':'Menu',
                                          'menuBarName':'menuRoot',
                                          'menuButtonName':'Struts Bonds',
                                          'menuEntryLabel':'Set Params + Build',}
#                                          'menuCascadeName':'Build'}


BuildStrutsBondsGUICommandGUI = CommandGUI()
BuildStrutsBondsGUICommandGUI.addMenuCommand('menuRoot', 'Struts Bonds', 
                                               'Set Parms + Build',)# cascadeName = 'Build')


class BuildStrutsBonds(MVCommand):
    """This command finds hydrogen donor atoms within 2.4*percentCutoff angstrom distance of hydrogen acceptor atoms. It builds and returns a dictionary atDict whose keys are hydrogen atoms (or hydrogenbond donor atoms if there are no hydrogens) and whose values are potential h-bond acceptors and distances to these atoms, respectively
    \nPackage : Pmv
    \nModule  : StrutsCommands
    \nClass   : BuildStrutsBonds 
    \nCommand : buildStruts
    \nSynopsis:\n
        atDict <- buildStruts(group, paramDict, **kw)
    \nRequired Arguments:\n       
        group1 ---  atoms\n 
        group2 --- atoms\n 
        paramDict --- a dictionary with these keys and default values\n
        keywords --\n
            distCutoff: 2.25  strutSpacingMinimum\n
            distCutoff2: 3.00 strutLengthMaximum\n
    """


#    def onAddCmdToViewer(self):
#        self.distSelector = DistanceSelector(return_dist=0)
#        if not self.vf.commands.has_key('typeAtoms'):
#            self.vf.loadCommand('editCommands', 'typeAtoms', 'Pmv',
#                                topCommand=0)


    def reset(self):
        ct = 0
        for at in self.vf.allAtoms:
            if hasattr(at, 'struts'):
                for item in at.struts:
                    del item
                    ct = ct +1
                delattr(at, 'struts')
        #print 'reset: deleted  hbonds from ' + str(ct)+ ' atoms '


    def doit(self, group1, paramDict, reset):
        st = StrutsBondBuilder()
        vStruts = st.build(group1,reset=reset, paramDict=paramDict)
        return vStruts

    def __call__(self, group1, paramDict={}, reset=1,  **kw):
        """atDict <--- buildHbonds(group1, group2, paramDict, **kw)
           \ngroup1 ---  atoms 
           \nparamDict --- a dictionary with these keys and default values
           \nkeywprds ---\n
           \ndistCutoff: 2.25  hydrogen--acceptor distance
           \ndistCutoff2: 3.00 donor... acceptor distance
           """
        group1 = self.vf.expandNodes(group1)
        if not (len(group1) ):
            return 'ERROR'
        #for item in [group1, group2]:
        if group1.__class__!=Atom:
                group1 = group1.findType(Atom)

        if not paramDict.has_key('distCutoff'):
            paramDict['distCutoff'] = 6
        if not paramDict.has_key('distCutoff2'):
            paramDict['distCutoff2'] = 5.0
        return apply( self.doitWrapper, (group1, paramDict, reset), kw)


class DisplayStruts(MVCommand):
    """  
   * Display and Return a vector of support posts for rapid prototyping models 
   * along the lines of George Phillips for Pymol except on actual molecular
   * segments (biopolymers), not PDB chains (which may or may not be
   * continuous). => work actually on chain
 
   \nPackage : Pmv
   \nModule  : strutsCommands
   \nClass   : DisplayStruts
   \nCommand : displayStruts
   \nSynopsis:\n
        None <--- displayStruts(node)
    """

    def __init__(self, func=None):
        MVCommand.__init__(self, func)
        self.flag = self.flag | self.objArgOnly

    def initGeom(self):
        #initialize:
        #   self.geom
        #   self.hasGeom
        pass


    def onAddCmdToViewer(self):
        self.verts = []  
        if self.vf.hasGui:
            self.initGeom()
            #from DejaVu.Labels import Labels
          
            self.showAll = Tkinter.IntVar()
            self.showAll.set(1)
            self.vf.loadModule('labelCommands', 'Pmv', log=0)
            # Create a ColorChooser.
            self.palette = ColorChooser(commands=self.color_cb,
                    exitFunction = self.hidePalette_cb)
            # pack
            self.palette.pack(fill='both', expand=1)
            # hide it 
            self.palette.hide()
        self.showAll = None
        self.width = 100
        self.height = 100
        self.winfo_x = None
        self.winfo_y = None

    def hidePalette_cb(self, event=None):
        self.palette.hide()

    def reset(self):
        self.geom.Set(vertices=[], tagModified=False)
        self.vf.GUI.VIEWER.Redraw()
        self.hasGeom = 0


    def update(self, event=None):
        self.radii = self.radii_esw.get()
        self.hasGeom =0
        self.showAllStruts()
        
    def color_cb(self, colors):
        from DejaVu import colorTool
        self.geom.Set(materials = (colors[:3],), tagModified=False)
        self.vf.GUI.VIEWER.Redraw()

    def changeColor(self, event=None):
        #col = self.palette.display(callback=self.color_cb, modal=1)
        #self.palette.pack(fill='both', expand=1)
        # Create a ColorChooser.
        if not hasattr(self, 'palette'):
            self.palette = ColorChooser(commands=self.color_cb,
                        exitFunction = self.hidePalette_cb)
            # pack
            self.palette.pack(fill='both', expand=1)
            # hide it 
            self.palette.hide()
        else:
            self.palette.master.deiconify()

    def getIfd(self, atNames):
        #base class
        pass

    def setUpWidgets(self, atNames):
        if not hasattr(self, 'ifd'):
            self.getIfd(atNames)
        self.radii_esw = self.ifd.entryByName['radii']['widget']
        self.lb = self.ifd.entryByName['atsLC']['widget'].lb


    def doit(self, ats):
        #DisplayStruts base class
        self.reset()
        hbats = AtomSet(ats.get(lambda x: hasattr(x, 'struts')))
        if not hbats:
            self.warningMsg('no struts bonds found, please compute them')
            return 'ERROR'
        self.hats = hbats
        self.showAllHBonds()


    def updateQuality(self, event=None):
        # asSpheres
        self.quality = self.quality_sl.get()
        self.geom.Set(quality=quality, tagModified=False)
        self.showAllHBonds()


    def dismiss_cb(self, event=None, **kw):
        # base class
        self.reset()
        try:
            self.width = str(self.toplevel.winfo_width())
            self.height = str(self.toplevel.winfo_height())
            self.winfo_x = str(self.toplevel.winfo_x())
            self.winfo_y = str(self.toplevel.winfo_y())
        except:
            pass
        self.vf.GUI.VIEWER.Redraw()
        if hasattr(self, 'ifd'):
            delattr(self, 'ifd')
        if hasattr(self, 'form2'):
            self.form2.destroy()
            delattr(self, 'form2')
        if hasattr(self, 'form'):
            self.form.destroy()
            delattr(self, 'form')
        if hasattr(self, 'palette'):
            #self.palette.exit()
            self.palette.hide()


    def setupDisplay(self):
        #draw geom between hAts OR donAts and accAts
        self.geom.Set(vertices = self.verts, radius = self.radius,
                      tagModified=False)
        self.vf.GUI.VIEWER.Redraw()


    def interpolate(self, pt1, pt2):
        # self.spacing = .4
        length = dist(pt1, pt2)
        c1 = Numeric.array(pt1)
        c2 = Numeric.array(pt2)
        n = length/self.spacing
        npts = int(math.floor(n))
        # use floor of npts to set distance between > spacing
        delta = (c2-c1)/(1.0*npts)
        ##spacing = length/floor(npts)
        vertList = []
        for i in range(npts):
            vertList.append((c1+i*delta).tolist())
        vertList.append(pt2.tolist())
        return vertList


    def setDVerts(self, entries, event=None):
        if not hasattr(self, 'ifd2'):
            self.changeDVerts()
        lb = self.ifd2.entryByName['datsLC']['widget'].lb
        if lb.curselection() == (): return
        atName = lb.get(lb.curselection())
        ind = int(lb.curselection()[0])
        for h in self.hats:
            for b in h.hbonds:
                ats = b.donAt.parent.atoms.get(lambda x, atName=atName: x.name==atName)
                if ats is None or len(ats) == 0:
                    if b.hAt is not None: at = b.hAt
                    else: at = b.donAt
                else:
                    at = ats[0]
                b.spVert1 = at
        self.hasGeom = 0
        self.showAllHBonds()
        

    def setAVerts(self, entries, event=None):
        if not hasattr(self, 'ifd2'):
            self.changeDVerts()
        lb = self.ifd2.entryByName['aatsLC']['widget'].lb
        if lb.curselection() == (): return
        atName = lb.get(lb.curselection())
        ind = int(lb.curselection()[0])
        for h in self.hats:
            for b in h.hbonds:
                ats = b.accAt.parent.atoms.get(lambda x, atName=atName: x.name==atName)
                if ats is None or len(ats) == 0:
                    at = b.accAt
                else:
                    at = ats[0]
                b.spVert2 = at
        self.hasGeom = 0
        self.showAllHBonds()


    def changeDVerts(self, event=None):
        #for all residues in hbonds, pick new donorAttachment
        # and new acceptorAttachment
        entries = []
        ns = ['N','C','O','CA','reset']
        for n in ns:
            entries.append((n, None))

        if hasattr(self, 'form2'):
            self.form2.root.tkraise()
            return
        ifd2 = self.ifd2=InputFormDescr(title = 'Set Anchor Atoms')
        ifd2.append({'name': 'datsLC',
            'widgetType':ListChooser,
            'wcfg':{
                'entries': entries,
                'mode': 'single',
                'title': 'Donor Anchor',
                'command': CallBackFunction(self.setDVerts, entries),
                'lbwcfg':{'height':5, 
                    'selectforeground': 'red',
                    'exportselection': 0,
                    #'lbpackcfg':{'fill':'both', 'expand':1},
                    'width': 30},
            },
            'gridcfg':{'sticky':'wens', 'columnspan':2}})
        ifd2.append({'name': 'aatsLC',
            'widgetType':ListChooser,
            'wcfg':{
                'entries': entries,
                'mode': 'single',
                'title': 'Acceptor Anchor',
                'command': CallBackFunction(self.setAVerts, entries),
                'lbwcfg':{'height':5, 
                    'selectforeground': 'red',
                    #'lbpackcfg':{'fill':'both', 'expand':1},
                    'exportselection': 0,
                    'width': 30},
            },
            'gridcfg':{'sticky':'wens', 'columnspan':2}})
        ifd2.append({'name':'doneBut',
            'widgetType':Tkinter.Button,
            'wcfg': { 'text':'Done',
                'command': self.closeChangeDVertLC},
            'gridcfg':{'sticky':'wens'}})
        self.form2 = self.vf.getUserInput(self.ifd2, modal=0, blocking=0)
        self.form2.root.protocol('WM_DELETE_WINDOW',self.closeChangeDVertLC)


    def closeChangeDVertLC(self, event=None):
        if hasattr(self, 'ifd2'):
            delattr(self, 'ifd2')
        if hasattr(self, 'form2'):
            self.form2.destroy()
            delattr(self, 'form2')


    def showAllHBonds(self, event=None):
        pass
        #self.geom.Set(vertices = self.verts, radii = self.radii,
        #              tagModified=False)
        #self.vf.GUI.VIEWER.Redraw()


    def guiCallback(self):
        #showHbonds
        if not len(self.vf.Mols):
            self.warningMsg('no molecules in viewer')
            return 
        sel =  self.vf.getSelection()
        #put a selector here
        if len(sel):
            ats = sel.findType(Atom)
            apply(self.doitWrapper, (ats,), {})



class DisplayStrutsAsSpheres(DisplayStruts):
    """This class allows user to visualize pre-existing HydrogenBonds between 
    atoms in viewer as small spheres
    \nPackage : Pmv
   \nModule  : hbondCommands
   \nClass   : DisplayHBondsAsSpheres
   \nCommand : displayHBSpheres
   \nSynopsis:\n
        None <--- displayHBSpheres(nodes, **kw)
    """

    def initGeom(self):
        from DejaVu.IndexedPolylines import IndexedPolylines
        #from DejaVu.Labels import Labels
        self.quality = 4
        self.spheres = self.geom = Spheres('strutsSpheres', 
                    materials=((0,1,0),), shape=(0,3),
                    radii=0.1, quality=4, pickable=0, inheritMaterial=0, protected=True)
        geoms = [self.spheres]
        self.masterGeom = Geom('strutsAsSpheresGeoms',shape=(0,0), 
                                pickable=0, protected=True)
        self.masterGeom.isScalable = 0
        if self.vf.hasGui:
            miscGeom = self.vf.GUI.miscGeom
            hbond_geoms = check_hbond_geoms(self.vf.GUI)
        
            self.vf.GUI.VIEWER.AddObject(self.masterGeom, parent=hbond_geoms)
            for item in geoms:
                self.vf.GUI.VIEWER.AddObject(item, parent=self.masterGeom)
        self.hasGeom = 0
        self.spacing = .40
        self.radii = 0.1
        self.verts = []
        

    def adjustVerts(self, v1, v2, length):
        #each end needs to be changed by length/2.
        #eg if length = 1.1, change each end by .05
        if length==self.oldlength:
            return (v1, v2)
        vec = Numeric.array(v2) - Numeric.array(v1)
        vec_len = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2) 
        alpha = (length-1.)/2.  #(.5-1)/2.-> -.25%  or (1.5 -1.)/2. ->+.25%
        #delta v1 is v1 - alpha*vec_len
        #delta v2 is v2 + alpha*vec_len
        delta = alpha*vec_len
        return Numeric.array(v1-delta*vec).astype('f'), Numeric.array(v2+delta*vec).astype('f')

    def __call__(self, nodes, **kw):
        """None <- displayHBSpheres(nodes, **kw) """
        if type(nodes) is StringType:
            self.nodeLogString = "'"+nodes+"'"
        nodes = self.vf.expandNodes(nodes)
        if not len(nodes): return 'ERROR'
        ats = nodes.findType(Atom)
        apply(self.doitWrapper, (ats,), kw)


    def update(self, event=None):
        #as spheres
        self.radii = self.radii_esw.get()
        self.spacing = self.spacing_esw.get()
        self.hasGeom = 0
        self.showAllHBonds()
        

    def color_cb(self, colors):
        from DejaVu import colorTool
        self.geom.Set(materials = (colors[:3],), tagModified=False)
        self.vf.GUI.VIEWER.Redraw()
        col = colorTool.TkColor(colors[:3])
        self.quality_sl.config(troughcolor = col)


    def getIfd(self, atNames):
        #print 'in spheres getIfd'
        if not hasattr(self, 'ifd'):
            ifd = self.ifd=InputFormDescr(title = 'Show Hydrogen Bonds as Spheres')
            ifd.append({'name': 'hbondLabel',
                'widgetType': Tkinter.Label,
                'wcfg':{'text': str(len(atNames)) + ' Atoms in hbonds:\n(1=visible, 0 not visible)'},
                'gridcfg':{'sticky': 'wens', 'columnspan':2}})
            ifd.append({'name': 'atsLC',
                'widgetType':ListChooser,
                'wcfg':{
                    'entries': atNames,
                    'mode': 'multiple',
                    'title': '',
                    'command': CallBackFunction(self.showHBondLC, atNames),
                    'lbwcfg':{'height':5, 
                        'selectforeground': 'red',
                        'exportselection': 0,
                        'width': 30},
                },
                'gridcfg':{'sticky':'wens', 'row':2,'column':0, 'columnspan':2}})
            ifd.append( {'name':'spacing',
                'widgetType': ExtendedSliderWidget,
                'wcfg':{'label':'spacing',
                     'minval':.01, 'maxval':1.0,
                    'immediate':1,
                    'init':.4,
                    'width':150,
                    'command':self.update,
                    'sliderType':'float',
                    'entrypackcfg':{'side':'bottom'}},
                'gridcfg':{'sticky':'wens'}})
            ifd.append( {'name':'radii',
                'widgetType': ExtendedSliderWidget,
                'wcfg':{'label':'radii',
                     'minval':.01, 'maxval':1.0,
                    'immediate':1,
                    'init':.1,
                    'width':150,
                    'command':self.update,
                    'sliderType':'float',
                    'entrypackcfg':{'side':'bottom'}},
                'gridcfg':{'sticky':'wens','row':-1, 'column':1}})
            ifd.append( {'name':'quality',
                'widgetType': Tkinter.Scale,
                'wcfg':{'label':'quality',
                    'troughcolor':'green',
                     'from_':2, 'to_':20,
                    'orient':'horizontal',
                    'length':'2i',
                    'command':self.updateQuality },
                'gridcfg':{'sticky':'wens'}})
            ifd.append({'name':'changeColorBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Choose color',
                    'relief':'flat',
                    'command': self.changeColor},
                'gridcfg':{'sticky':'wes', 'row':-1, 'column':1}})
            ifd.append({'name':'changeVertsBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Set anchors',
                    'command': self.changeDVerts},
                'gridcfg':{'sticky':'wens'}})
            ifd.append({'name':'closeBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Dismiss',
                    'command': self.dismiss_cb},
                'gridcfg':{'sticky':'wens', 'row':-1, 'column':1}})


    def setUpWidgets(self, atNames):
        if not hasattr(self, 'ifd'):
            self.getIfd(atNames)
        self.radii_esw = self.ifd.entryByName['radii']['widget']
        self.spacing_esw = self.ifd.entryByName['spacing']['widget']
        self.quality_sl= self.ifd.entryByName['quality']['widget']
        self.quality_sl.set(self.quality)
        self.lb = self.ifd.entryByName['atsLC']['widget'].lb


    def updateQuality(self, event=None):
        self.quality = self.quality_sl.get()
        self.geom.Set(quality=self.quality, tagModified=False)
        self.vf.GUI.VIEWER.Redraw()

    def showAllHBonds(self, event=None):
        if not self.hasGeom:
            verts = []
            faces = []
            ct = 0
            for at in self.hats:
                for b in at.struts:
                    pt1 = getTransformedCoords(b.donAt)
                    at2 = b.accAt
                    pt2 = getTransformedCoords(at2)
                    #verts.extend([pt1, pt2])
                    verts.extend(self.interpolate(pt1, pt2))
#                    faces.append((ct, ct+1))
#                    ct = ct + 2
            #reset oldlength here, after recalc all hbond verts
#            self.oldlength = self.length
            self.verts = verts
#            self.faces = faces
            self.hasGeom  = 1

        self.spheres.Set(vertices=self.verts, radii=self.radii,
                            tagModified=False)
        self.vf.GUI.VIEWER.Redraw()
DisplayStrutsAsSpheresGuiDescr = {'widgetType':'Menu',
                                          'menuBarName':'menuRoot',
                                          'menuButtonName':'Struts Bonds',
                                          'menuEntryLabel':'As Spheres',
                                          'menuCascadeName': 'Display'}


DisplayStrutsAsSpheresGUI = CommandGUI()
DisplayStrutsAsSpheresGUI.addMenuCommand('menuRoot', 'Struts Bonds',
        'As Spheres', cascadeName = 'Display')



class DisplayStrutsAsCylinders(DisplayStruts):
    """This class allows user to visualize pre-existing HydrogenBonds between 
atoms in viewer as cylinders
   \nPackage : Pmv
   \nModule  : hbondCommands
   \nClass   : DisplayHBondsAsCylinders
   \nCommand : displayHBCylinders
   \nSynopsis:\n
        None <- displayHBCylinders(nodes, **kw)
    """


    def initGeom(self):
        self.cylinders = self.geom = Cylinders('hbondCylinders', 
                    quality=40, culling=GL.GL_NONE, radii=(0.2),
                    materials=((0,1,0),), pickable=0, inheritMaterial=0)
        #DejaVu.Cylinders overwrites kw cull so have to reset it here
        self.cylinders.culling = GL.GL_NONE
        geoms = [self.cylinders]
        miscGeom = self.vf.GUI.miscGeom
        hbond_geoms = check_hbond_geoms(self.vf.GUI)
        self.masterGeom = Geom('StrutsAsCylindersGeoms',shape=(0,0), 
                                pickable=0, protected=True)
        self.vf.GUI.VIEWER.AddObject(self.masterGeom, parent=hbond_geoms)
        for item in geoms:
            self.vf.GUI.VIEWER.AddObject(item, parent=self.masterGeom)
        self.hasGeom = 0
        self.radii = 0.2
        self.length = 1.0
        self.oldlength = 1.0
        self.verts = []
        self.faces = []


    def __call__(self, nodes, **kw):
        """None <- displayHBCylinders(nodes, **kw) """
        if type(nodes) is StringType:
            self.nodeLogString = "'"+nodes+"'"
        nodes =self.vf.expandNodes(nodes)
        if not len(nodes): return 'ERROR'
        ats = nodes.findType(Atom)
        apply(self.doitWrapper, (ats,), kw)


    def getIfd(self, atNames):
        #cylinders
        if not hasattr(self, 'ifd'):
            ifd = self.ifd = InputFormDescr(title='Show Hydrogen Bonds as Cylinders')
            ifd.append({'name': 'hbondLabel',
                'widgetType': Tkinter.Label,
                'wcfg':{'text': str(len(atNames)) + ' Atoms in hbonds:\n(1=visible, 0 not visible)'},
                'gridcfg':{'sticky': 'wens', 'columnspan':2}})
            ifd.append({'name': 'atsLC',
                'widgetType':ListChooser,
                'wcfg':{
                    'entries': atNames,
                    'mode': 'multiple',
                    'title': '',
                    'command': CallBackFunction(self.showHBondLC, atNames),
                    'lbwcfg':{'height':5, 
                        'selectforeground': 'red',
                        'exportselection': 0,
                        'width': 30},
                },
                'gridcfg':{'sticky':'wens', 'row':2,'column':0, 'columnspan':2}})
            ifd.append( {'name':'radii',
                'widgetType': ExtendedSliderWidget,
                'wcfg':{'label':'radii',
                     'minval':.01, 'maxval':1.0,
                    'immediate':1,
                    'init':.2,
                    'width':250,
                    'command':self.update,
                    'sliderType':'float',
                    'entrypackcfg':{'side':'right'}},
                'gridcfg':{'sticky':'wens', 'columnspan':2}})
            ifd.append( {'name':'length',
                'widgetType': ExtendedSliderWidget,
                'wcfg':{'label':'length',
                     'minval':.01, 'maxval':5.0,
                    'immediate':1,
                    'init':1.0,
                    'width':250,
                    'command':self.update,
                    'sliderType':'float',
                    'entrypackcfg':{'side':'right'}},
                'gridcfg':{'sticky':'wens', 'columnspan':2}})
            ifd.append({'name':'changeVertsBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Set anchors',
                    'command': self.changeDVerts},
                'gridcfg':{'sticky':'wens'}})
            ifd.append({'name':'changeColorBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Change color',
                    'command': self.changeColor},
                'gridcfg':{'sticky':'wes', 'row':-1, 'column':1}})
            ifd.append({'name':'closeBut',
                'widgetType':Tkinter.Button,
                'wcfg': { 'text':'Dismiss',
                    'command': self.dismiss_cb},
                'gridcfg':{'sticky':'wens','columnspan':2 }})
            #ifd.append({'name':'changeVertsBut',
                #'widgetType':Tkinter.Button,
                #'wcfg': { 'text':'Set anchors',
                    #'command': self.changeDVerts},
                #'gridcfg':{'sticky':'wens'}})


    def setUpWidgets(self, atNames):
        if not hasattr(self, 'ifd'):
            self.getIfd(atNames)
        self.radii_esw = self.ifd.entryByName['radii']['widget']
        self.length_esw = self.ifd.entryByName['length']['widget']
        self.lb = self.ifd.entryByName['atsLC']['widget'].lb



    def update(self, event=None):
        #as cylinders
        self.radii = self.radii_esw.get()
        self.oldlength = self.length
        self.length = self.length_esw.get()
        self.hasGeom = 0
        self.showAllHBonds()
        

    def adjustVerts(self, v1, v2, length):
        #each end needs to be changed by length/2.
        #eg if length = 1.1, change each end by .05
        if length==self.oldlength:
            return (v1, v2)
        vec = Numeric.array(v2) - Numeric.array(v1)
        vec_len = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2) 
        alpha = (length-1.)/2.  #(.5-1)/2.-> -.25%  or (1.5 -1.)/2. ->+.25%
        #delta v1 is v1 - alpha*vec_len
        #delta v2 is v2 + alpha*vec_len
        delta = alpha*vec_len
        return Numeric.array(v1-delta*vec).astype('f'), Numeric.array(v2+delta*vec).astype('f')


    def showAllHBonds(self, event=None):
        #can we use pyubic for this function?
        if not self.hasGeom:
            verts = []
            faces = []
            ct = 0
            for at in self.hats:
                for b in at.struts:
                    pt1 = getTransformedCoords(b.donAt)
                    at2 = b.accAt
                    pt2 = getTransformedCoords(at2)
                    #verts.extend([pt1, pt2])
                    verts.extend(self.adjustVerts(pt1, pt2, self.length))
                    faces.append((ct, ct+1))
                    ct = ct + 2
            #reset oldlength here, after recalc all hbond verts
            self.oldlength = self.length
            self.verts = verts
            self.faces = faces
            self.hasGeom  = 1

        self.cylinders.Set(vertices=self.verts, radii=self.radii,
                           faces=self.faces, tagModified=False)
        if self.vf.hasGui:
            self.vf.GUI.VIEWER.Redraw()

        


DisplayStrutsAsCylindersGuiDescr = {'widgetType':'Menu',
                                          'menuBarName':'menuRoot',
                                          'menuButtonName':'Struts Bonds',
                                          'menuEntryLabel':'As Cylinders',
                                          'menuCascadeName': 'Display'}


DisplayStrutsAsCylindersGUI = CommandGUI()
DisplayStrutsAsCylindersGUI.addMenuCommand('menuRoot', 'Struts Bonds',
        'As Cylinders', cascadeName = 'Display')


commandList=[
    {'name':'buildSBondsGC','cmd':BuildStrutsBondsGUICommand(),
            'gui': BuildStrutsBondsGUICommandGUI},
    {'name':'buildStruts','cmd':BuildStrutsBonds(), 'gui': None},
    {'name':'strutsAsSpheres','cmd':DisplayStrutsAsSpheres(),
            'gui':DisplayStrutsAsSpheresGUI},
    {'name':'strutsAsCylinders','cmd':DisplayStrutsAsCylinders(),
            'gui':DisplayStrutsAsCylindersGUI},
    ]



def initModule(viewer):
    for dict in commandList:
        viewer.addCommand(dict['cmd'], dict['name'], dict['gui'])
#self.browseCommands('strutsCommands', package='Pmv', topCommand=0)