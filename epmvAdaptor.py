"""
    Copyright (C) <2010>  Autin L.

    This file ePMV_git/epmvAdaptor.py is part of ePMV.

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
"""
The ePMV Adaptor Module

The ePMV Adaptor Module
=======================

This module provides the function to start ePMV, the function that handle the molecule loading, and
the Adaptor base class.
"""

# fixFile "/local/ludo/Desktop/blender-2.49b/MGLToolsPckgs/ePMV/blender/v24/blenderAdaptor.py",
# line 301, in updateMolAtomCoordLines KeyError: 'hsg1:A_line'



import sys, os
import platform
import DejaVu

DejaVu.enableVertexArray = False
from Pmv.mvCommand import MVCommand
from Pmv.moleculeViewer import MoleculeViewer
from Pmv.moleculeViewer import DeleteGeomsEvent, AddGeomsEvent, EditGeomsEvent
from Pmv.moleculeViewer import DeleteAtomsEvent, EditAtomsEvent
from Pmv.deleteCommands import BeforeDeleteMoleculesEvent, AfterDeleteAtomsEvent
from Pmv.displayCommands import BindGeomToMolecularFragment
from Pmv.trajectoryCommands import PlayTrajectoryCommand

from Pmv.pmvPalettes import AtomElements
from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
from Pmv.pmvPalettes import Shapely
from Pmv.pmvPalettes import SecondaryStructureType

from MolKit.protein import ResidueSetSelector, Chain, Protein, Residue, ChainSet
from MolKit.molecule import Atom, AtomSet

from mglutil.util.recentFiles import RecentFiles

import numpy
import numpy.oldnumeric as Numeric  # backward compatibility
import math
import ePMV
from ePMV import comput_util as util
from ePMV.installer import Installer
from ePMV.lightGridCommands import addGridCommand
from ePMV.lightGridCommands import readAnyGrid
from ePMV.lightGridCommands import IsocontourCommand
# TODO:
# add computation (trajectory reading,energy,imd,pyrosetta?,amber)
# check if work with server/client mode...

# color utility from pyubi
from upy import colors as col


def is_os_64bit():
    return platform.machine().endswith('64')


arch = "32bit"
if platform.architecture()[0] == '64bit':
    if platform.machine().endswith('64'):  # sys.maxint == 9223372036854775807:
        arch = "64bit"


# retrieve architecture os

class loadMoleculeInHost(MVCommand):
    """
    Command call everytime a molecule is read in PMV. Here is define whats happen
    in the hostApp when a molecule is add in PMV.ie creating hierarchy, empty
    parent optional pointCloud object, camera, light, etc...
    """

    def __init__(self, epmv):
        """
        constructor of the command.

        @type  epmv: epmvAdaptor
        @param epmv: the embeded PMV object which consist in the adaptor, the molecular
        viewer and the helper.
        """
        MVCommand.__init__(self)
        self.mv = epmv.mv
        self.epmv = epmv

    def checkDependencies(self, vf):
        from bhtree import bhtreelib

    def doit(self, mol, **kw):
        """
        actual function of the command.

        @type  mol: MolKit molecule
        @param mol: the molecule loaded in PMV

        @type  kw: dictionary
        @param kw: the dictionary of optional keywords arguments
        """
        #        sys.stderr.write('loadMolecule in host\n')
        print (".............loadMolecule..................")
        chname = ['Z', 'Y', 'X', 'W', 'V', 'U', 'T']
        molname = mol.name  # mol.replace("'","")
        # setup some variable
        self.mv.molDispl[molname] = {}
        for k in ["bead", "cpk", "bs", "ss", "loft", "arm", "spline", "surf",
                  "cms", "meta", "points", "lines", "cgeom"]:
            self.mv.molDispl[molname][k] = False
        self.mv.molDispl[molname]["col"] = None
        if molname not in list(self.mv.MolSelection.keys()):
            self.mv.MolSelection[molname] = {}
        if molname not in list(self.mv.selections.keys()):
            self.mv.selections[molname] = {}
        if molname not in list(self.mv.iMolData.keys()):
            self.mv.iMolData[molname] = []
        sc = self.epmv._getCurrentScene()
        # mol=os.path.splitext(os.path.basename(mol))[0]
        # sys.stderr.write('%s\n'%molname)
        if self.epmv.duplicatemol:  # molecule already loaded,so the name is overwrite by pmv, add _ind
            #            print self.epmv.duplicatedMols.keys()
            if mol in list(self.epmv.duplicatedMols.keys()):
                self.epmv.duplicatedMols[molname] += 1
            else:
                self.epmv.duplicatedMols[molname] = 1
            molname = molname + "_" + str(self.epmv.duplicatedMols[molname])
        molname = molname.replace(".", "_")
        # sys.stderr.write('%s\n'%mol)
        #        print self.mv.Mols.name
        P = mol = self.mv.getMolFromName(molname)
        if mol == None:
            #    print "WARNING RMN MODEL OR ELSE, THERE IS SERVERAL MODEL IN THE
            #    FILE\nWE LOAD ONLY LOAD THE 1st\n",self.Mols.name
            P = mol = self.mv.getMolFromName(molname + "_model1")
            mol.name = molname
        # mol=mol.replace("_","")
        print('read %s\n' % mol)
        # mol.name = mol.name.replace("_","")
        if self.epmv.build_bonds:
            import MolKit
            MolKit.bonds_threshold = self.epmv.bonds_threshold
            # if ciff and have bon information, use it.
            if not hasattr(mol, "mmCIF_dict"):
                self.mv.buildBondsByDistance(mol, log=0)
            #        self.mv.computeSESAndSASArea(mol,log=0)
            #        sys.stderr.write("center")
        center = mol.getCenter()
        #        sys.stderr.write(center)
        # if centering is need we will translate to center
        centerO = None
        if self.epmv.center_mol:  # and not self.epmv.parseBioMT:
            matrix = numpy.identity(4, 'f')
            matrix[3, :3] = numpy.array(center) * -1
            # print matrix
            vt = util.transformedCoordinatesWithMatrice(mol, matrix.transpose())
            mol.allAtoms.updateCoords(numpy.array(vt).tolist(), ind=0)
            # mol.allAtoms.setConformation(0)
            center = mol.getCenter()
            # print center
        else:
            # create an empty at center
            centerO = self.epmv._newEmpty(mol.name + "_center", location=center)  # center)
        if self.epmv.host == 'chimera':
            model = self.epmv.helper.readMol(mol.parser.filename)
            mol.ch_model = model
            mol.geomContainer.masterGeom.obj = model
            return
        if self.epmv.useModeller:
            #            print "ok add a conf"
            # add a conformation for modeller
            mol.allAtoms.addConformation(mol.allAtoms.coords[:])
            iConf = len(mol.allAtoms[0]._coords) - 1
            from ePMV.extension.Modeller.pmvAction import pmvAction
            mol.pmvaction = pmvAction(1, 1, 1000, iconf=iConf, pmvModel=mol,
                                      mv=self.epmv.mv, epmv=self.epmv)
            mol.allAtoms.setConformation(0)
        # skip,first,last
        else:
            if self.epmv.removeWater:
                self.mv.deleteWater(mol)
        # create an empty/null object as the parent of all geom, and build the
        # molecule hierarchy as empty for each Chain
        master = self.epmv._newEmpty(mol.name, location=[0., 0., 0.])  # center)
        mol.geomContainer.masterGeom.obj = master
        self.epmv._addObjectToScene(sc, master)
        if not self.epmv.center_mol and centerO is not None:
            self.epmv._addObjectToScene(sc, centerO, parent=master)
        mol.geomContainer.masterGeom.chains_obj = {}
        mol.geomContainer.masterGeom.res_obj = {}
        #        if self.epmv.doCloud:
        #            cloud = self.epmv._PointCloudObject(mol.name+"_cloud",
        #                                            vertices=mol.allAtoms.coords,
        #                                            parent=master)
        ch_colors = self.mv.colorByChains.palette.lookup(mol.chains)
        for i, ch in enumerate(mol.chains):
            sys.stderr.write(str(i) + "\n")
            # how to fix this problem...?
            if self.epmv.host == 'maya':
                if ch.name == " " or ch.name == "":
                    # this dont work with stride....name of chain dont stay for ss
                    ch.name = chname[i]
            ch_center = [0., 0., 0.]  # util.getCenter(ch.residues.atoms.coords)
            chobj = self.epmv._newEmpty(ch.full_name(), location=ch_center)  # ,parentCenter=center)
            mol.geomContainer.masterGeom.chains_obj[ch.name] = self.epmv._getObjectName(chobj)
            self.epmv._addObjectToScene(sc, chobj, parent=master, centerRoot=True)
            parent = chobj
            # make the chain material
            ch.material = self.epmv.helper.addMaterial(ch.full_name() + "_mat", ch_colors[i])
            ch.material = ch.full_name() + "_mat"
            #            if self.epmv.doCloud:
            #                print "ok docloud",ch.full_name()+"_cloud"
            #                cloud = self.epmv._PointCloudObject(ch.full_name()+"_cloud",
            #                                                vertices=ch.residues.atoms.coords,
            #                                                parent=chobj)
            # self.epmv._addObjectToScene(sc,cloud,parent=chobj)
            # if self.useTree == 'perRes' :
            #        for res in ch.residues :
            #            res_obj = util.makeResHierarchy(res,parent,useIK='+str(self.useIK)+')
            #            mol.geomContainer.masterGeom.res_obj[res.name]=util.getObjectName(res_obj)
            # elif self.useTree == 'perAtom' :
            #        for res in ch.residues :
            #            parent = util.makeAtomHierarchy(res,parent,useIK='+str(self.useIK)+')
            # else :
            chobjcpk = self.epmv._newEmpty(ch.full_name() + "_cpk", location=ch_center)
            mol.geomContainer.masterGeom.chains_obj[ch.name + "_cpk"] = self.epmv._getObjectName(chobjcpk)
            self.epmv._addObjectToScene(sc, chobjcpk, parent=chobj, centerRoot=True)
            chobjballs = self.epmv._newEmpty(ch.full_name() + "_bs", location=ch_center)
            mol.geomContainer.masterGeom.chains_obj[ch.name + "_balls"] = self.epmv._getObjectName(chobjballs)
            self.epmv._addObjectToScene(sc, chobjballs, parent=chobj, centerRoot=True)
            chobjss = self.epmv._newEmpty(ch.full_name() + "_ss", location=ch_center)
            mol.geomContainer.masterGeom.chains_obj[ch.name + "_ss"] = self.epmv._getObjectName(chobjss)
            self.epmv._addObjectToScene(sc, chobjss, parent=chobj, centerRoot=True)

        #        if mol.parser.hasSsDataInFile():
        #            mod = "From File"
        #        else:
        #            mod = "From Pross"
        #        self.mv.computeSecondaryStructure(
        #            mol, molModes={'%s'%mol.name:mod}, topCommand=0)
        # self.mv.extrudeSecondaryStructure(sel, topCommand=0, log=0, display=0)
        self.epmv.testNumberOfAtoms(mol)
        self.mv.assignAtomsRadii(str(molname), united=0, log=0, overwrite=1)
        self.epmv._addMolecule(mol.name)
        radius = util.computeRadius(P, center)
        #        sys.stderr.write(str(radius))
        focal = 2. * math.atan((radius * 1.03) / 100.) * (180.0 / 3.14159265358979323846)
        #        sys.stderr.write(str(focal))
        center = center[0], center[1], (center[2] + focal * 2.0)
        #        if mol.parser.hasSsDataInFile():
        #            mod = "From File"
        #        else:
        #            mod = "From Pross"
        #        self.mv.computeSecondaryStructure(
        #            mol, molModes={'%s'%mol.name:mod}, topCommand=0)

        #        print center
        if self.epmv.doCamera:
            self.epmv._addCameraToScene("cam_" + mol.name, "ortho", focal, center, sc)
        if self.epmv.doLight:
            self.epmv._addLampToScene("lamp_" + mol.name, 'Area', (1., 1., 1.), 15., 0.8, 1.5, False, center, sc)
            self.epmv._addLampToScene("sun_" + mol.name, 'Sun', (1., 1., 1.), 15., 0.8, 1.5, False, center, sc)

            # parseBioMT: problem of centering....we should just center the big thing at the end
        #        if self.epmv.parseBioMT:
        #            #need to get the information from the parser and create the instance/null parent etc.
        #            #problem for maya and blender....
        #            #only for PDB actually
        #            #by default we can create the trnasformation node and then apply later the geometry...?

    def onAddObjectToViewer(self, obj):
        self.doitWrapper(*(obj,))

    def __call__(self, mol, **kw):
        self.doitWrapper(*(mol,), **kw)


class epmvAdaptor(object):
    """
    The ePMV Adaptor object
    =======================
            The base class for embedding pmv in a hostApplication
            define the hostAppli helper function to apply according Pmv event.
            Each hostApp adaptor herited from this class.
    """
    lastUsed = {}
    listeKeywords = {}
    listeKeywords["dsAtLoad"] = ["secondary structure", "beadRibbon", "clouds",
                                 "line", "MSMS", "CMS", "None"]
    keywords = {"useLog": None,
                "bicyl": {"name": "Split bonds (slower)", "value": True, "type": "checkbox"},
                # one or two cylinder to display a bond stick
                "center_mol": {"name": "Center molecule to origin", "value": True, "type": "checkbox"},
                "center_grid": {"name": "Center Grid", "value": True, "type": "checkbox"},
                "build_bonds": {"name": "Build bonds by distance, with", "value": True, "type": "checkbox"},
                "bonds_threshold": {"name": "bonds distance cutoff", "value": 1.1, "type": "inputFloat",
                                    "mini": 0., "maxi": 10., "label": "Minimum bond distance [A]:"},
                "joins": None,
                "uniq_ss": {"name": "Single colorizable mesh for Ribbon and Beaded Ribbon", "value": False,
                            "type": "checkbox"},
                "colorProxyObject": None,
                "only": None,
                "updateSS": None,
                "updateColor": {"name": "Update color automatically for multi-state models", "value": True,
                                "type": "checkbox"},
                "use_instances": {"name": "Build instances for atoms and bonds", "value": True, "type": "checkbox"},
                "duplicatemol": None,
                "useTree": None,  # None#'perRes' #or perAtom
                "useIK": None,
                "use_progressBar": {"name": "Progress bar", "value": False, "type": "checkbox"},
                # "doCloud":{"name":"Render points","value":True,"type":"checkbox"}, now in the represnetation
                "doCamera": {"name": "PMV camera", "value": False, "type": "checkbox"},
                "removeWater": {"name": "Remove water", "value": True, "type": "checkbox"},
                "dsAtLoad": {"name": "Loading display",
                             "label": "Default representation:",
                             "value": listeKeywords["dsAtLoad"],
                             "type": "pullMenu"},
                "join_ss": {"name": "Connect Ribbon geometry", "value": False, "type": "checkbox"},
                "force_pross": {"name": "Force PROSS (override pdb file SS)", "value": False, "type": "checkbox"},
                "doLight": {"name": "PMV light", "value": False, "type": "checkbox"},
                "useModeller": {"name": "Use Modeller", "value": False, "type": "checkbox"},
                "usePymol": {"name": "Use PyMOL", "value": False, "type": "checkbox"},
                # "parseBioMT":{"name":"Use PyMol","value":False,"type":"checkbox"},
                "synchro_realtime": {"name": "Viewport changes modify PDB data (Synchro realtime)", "value": False,
                                     "type": "checkbox"},
                "synchro_timeline": {"name": "Synchronize Data Player to host animation timeline with:",
                                     "value": False, "type": "checkbox"},
                "synchro_ratio": [{"name": "data steps for every", "value": 1, "type": "inputInt",
                                   "mini": 0, "maxi": 2000},
                                  {"name": "host animation frames", "value": 1, "type": "inputInt",
                                   "mini": 0, "maxi": 2000}],
                "forceFetch": {"name": "Override cache version when [Fetch]ing new molecule",
                               "value": False, "type": "checkbox"},
                "minmaxCMSgrid": [{"name": "mini cms gridstep", "value": 0, "type": "inputInt",
                                   "mini": 0, "maxi": 2000},
                                  {"name": "maxi cms gridstep", "value": 100, "type": "inputInt",
                                   "mini": 0, "maxi": 2000}],
                }

    # need keyword order

    def setupMV(self):
        print ("setupMV", sys.version_info, sys.version_info < (3, 0))
        self.mv.addCommand(BindGeomToMolecularFragment(), 'bindGeomToMolecularFragment', None)
        self.mv.browseCommands('trajectoryCommands', commands=['openTrajectory'], log=0, package='Pmv')
        self.mv.addCommand(PlayTrajectoryCommand(), 'playTrajectory', None)
        self.mv.addCommand(addGridCommand(), 'addGrid', None)
        self.mv.addCommand(readAnyGrid(), 'readAny', None)
        self.mv.addCommand(IsocontourCommand(), 'isoC', None)
        if sys.version_info < (3, 0):
            self.mv.browseCommands('colorCommands', package='ePMV.pmv_dev', topCommand=0)
        # self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        # self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        # define the listener
        if self.host is not None:
            self.mv.registerListener(DeleteGeomsEvent, self.updateGeom)
            self.mv.registerListener(AddGeomsEvent, self.updateGeom)
            self.mv.registerListener(EditGeomsEvent, self.updateGeom)
            self.mv.registerListener(AfterDeleteAtomsEvent, self.updateModel)
            self.mv.registerListener(BeforeDeleteMoleculesEvent, self.updateModel)
            self.mv.addCommand(loadMoleculeInHost(self), '_loadMol', None)
            # self.mv.embedInto(self.host,debug=0)
            self.mv.embeded = True
        # compatibility with PMV
        self.mv.Grid3DReadAny = self.mv.readAny
        # mv.browseCommands('superimposeCommandsNew', package='Pmv', topCommand=0)
        self.mv.userpref['Read molecules as']['value'] = 'conformations'
        self.mv.setUserPreference(('Read molecules as', 'conformations',), log=0)
        self.mv.setUserPreference(('Number of Undo', '0',), redraw=0, log=1)
        self.mv.setUserPreference(('Save Perspective on Exit', 'no',), log=0)
        self.mv.setUserPreference(('Transformation Logging', 'no',), log=0)
        # should add some user preferece and be able to save it
        # recentFiles Folder
        rcFile = self.mv.rcFolder
        if rcFile:
            rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
            self.mv.recentFiles = RecentFiles(self.mv, None, filePath=rcFile, index=0)
        else:
            print("no rcFolder??")

            # this  create mv.hostapp which handle server/client and log event system
            # NOTE : need to test it in the latest version
        #        if not self.useLog :
        #            self.mv.hostApp.driver.useEvent = True
        self.mv.iTraj = {}

        self.funcColor = [self.mv.colorByAtomType,
                          self.mv.colorAtomsUsingDG,
                          self.mv.colorByResidueType,
                          self.mv.colorResiduesUsingShapely,
                          self.mv.colorBySecondaryStructure,
                          self.mv.colorByChains,
                          self.mv.colorByDomains,
                          self.mv.color,
                          self.mv.colorByProperty]
        self.fTypeToFc = {"ByAtom": 0, "AtomsU": 1, "ByResi": 2, "Residu": 3,
                          "BySeco": 4, "ByChai": 5, "ByDoma": 6, "": 7,
                          "ByPropN": 8, "ByPropT": 9, "ByPropS": 10}
        self.mv.host = self.host
        self.mv.selectionLevel = Atom

    #        mv.hostApp.driver.bicyl = self.bicyl

    def __init__(self, mv=None, host="", useLog=False, debug=0, gui=False, **kw):
        """
        Constructor of the adaptor. Register the listener for PMV events and setup
        defaults options. If no molecular viewer are provided, start a fresh pmv
        session.

        @type  mv: MolecularViewer
        @param mv: a previous pmv cession gui-less
        @type  host: string
        @param host: name of the host application
        @type  useLog: boolean
        @param useLog: use Command Log event instead of Geom event (deprecated)
        @type  debug: int
        @param debug: debug mode, print verbose
        """

        self.mv = mv
        self.host = host
        self.soft = host
        self.rep = "epmv"
        if not hasattr(self, "helper"):
            self.helper = None
        #        self.Set(reset=True,useLog=useLog,**kw)
        if self.mv == None:
            self.mv = self.start(debug=debug)
        self.mv.helper = self.helper
        self.setupMV()
        self.addADTCommands()
        if not hasattr(self.mv, 'molDispl'): self.mv.molDispl = {}
        if not hasattr(self.mv, 'MolSelection'): self.mv.MolSelection = {}
        if not hasattr(self.mv, 'selections'): self.mv.selections = {}
        if not hasattr(self.mv, 'iMolData'): self.mv.iMolData = {}
        # options with default values
        self.duplicatedMols = {}
        self.env = None
        self.inst = None
        self.gui = None
        self.GUI = None
        self.timer = False
        self.mglroot = ""
        self.setupInst()
        self.ResidueSelector = ResidueSetSelector()
        self.ssk = ['Heli', 'Shee', 'Coil', 'Turn', 'Stra']
        self.ResidueSelector = ResidueSetSelector()
        self.AtmRadi = {"A": 1.54, "M": 1.54, "N": "1.7", "C": "1.74", "CA": "1.74",
                        "O": "1.39", "S": "1.85", "H": "1.2", "P": "1.04"}
        self.lookupDGFunc = util.lookupDGFunc
        self.max_atoms = 10000
        self.usefullname = False
        self.molDictionary = {}
        self.hmol = 0
        self.control_mmaya = False
        self.MAX_LENGTH_NAME = 20
        self.current_selection = None

    #        if self.host.find("blender") != -1 :
    #            self.MAX_LENGTH_NAME = 5#this for blender..you may change it for other host...

    def setupInst(self):
        #        print "mglroot ",self.mglroot
        if not self.mglroot:
            import Pmv
            dirP = Pmv.__path__[0]
            os.chdir(dirP)  # pmv
            os.chdir(".." + os.sep)  # MGLToolsPckgs
            os.chdir(".." + os.sep)  # mgltools
            self.mglroot = os.path.abspath(os.curdir)
        #            print "mglrootx ",self.mglroot
        if self.inst is None:
            self.inst = Installer(mgl=self.mglroot)
        else:
            self.inst.setMGL(mgl=self.mglroot)

    def initOption(self):
        """
        Initialise the defaults options for ePMV, e.g. keywords.
        """
        # we should use userpref from the ViewerFramework and mglutil.userpref class
        # saved in '/local/ludo/.mgltools/1.5.6rc3/.settings'
        for key in self.keywords:
            if self.keywords[key] is not None and key != "synchro_ratio" and key != "minmaxCMSgrid":
                if self.keywords[key]["type"] == "pullMenu":
                    val = self.listeKeywords[key][0]
                    setattr(self, key, val)
                else:
                    setattr(self, key, self.keywords[key]["value"])
        self.dsAtLoad = "secondary structure"  # default
        self.useLog = False
        self.joins = False
        self.colorProxyObject = False
        self.only = False
        self.updateSS = False
        #        self.use_instances=True
        self.duplicatemol = False
        self.useTree = 'default'  # None#'perRes' #or perAtom
        self.useIK = False
        self.useModeller = False  # do we use modeller
        self.usePymol = False
        self._modeller = False  # is modeller present
        self.synchro_ratio = [self.keywords["synchro_ratio"][0]["value"],
                              self.keywords["synchro_ratio"][0]["value"]]  # every 1 step for every 1 frame
        self._AF = False
        self._AR = False
        self._pymol = False
        self._prody = False
        self.doCamera = False
        self.synchronize()

    def Set(self, reset=False, **kw):
        """
        Set ePmv options provides by the keywords arguments.
        e.g. epmv.Set(bicyl=True)

        @type  reset: bool
        @param reset: reset to default values all options
        @type  kw: dic
        @param kw: list of options and their values.
        """
        if reset:
            self.initOption()

        for k in kw:
            if k in list(self.keywords.keys()):
                if self.keywords[k] is not None and k != "synchro_ratio" and k != "minmaxCMSgrid":
                    setattr(self, k, kw[k])
                    self.keywords[k]["value"] = kw[k]

        val = kw.pop('joins', None)
        if val is not None:
            self.joins = val
        val = kw.pop('colorProxyObject', None)
        if val is not None:
            self.colorProxyObject = val
        val = kw.pop('only', None)
        if val is not None:
            self.only = val
        val = kw.pop('updateSS', None)
        if val is not None:
            self.updateSS = val
        val = kw.pop('use_instances', None)
        if val is not None:
            self.use_instances = val
        val = kw.pop('duplicatemol', None)
        if val is not None:
            self.duplicatemol = val
        val = kw.pop('useTree', None)
        if val is not None:
            self.useTree = val
        val = kw.pop('useIK', None)
        if val is not None:
            self.useIK = val
        val = kw.pop('useModeller', None)
        if val is not None:
            self.useModeller = val
        val = kw.pop('usePymol', None)
        if val is not None:
            self.usePymol = val
        val = kw.pop('synchro_ratio', None)
        if val is not None:
            self.synchro_ratio = val
            # should be a an array [1,1]
        val = kw.pop('usefullname', None)
        if val is not None:
            self.usefullname = val

    def start(self, debug=0):
        """
        Initialise a PMV guiless session. Load specific command to PMV such as
        trajectory, or grid commands which are not automatically load in the
        guiless session.

        @type  debug: int
        @param debug: debug mode, print verbose

        @rtype:   MolecularViewer
        @return:  a PMV object session.
        """
        customizer = ePMV.__path__[0] + os.sep + "epmvrc.py"
        #        print "customizer ",customizer
        # replace _pmvrc ?
        mv = MoleculeViewer(logMode='overwrite', customizer=customizer,
                            master=None, title='pmv', withShell=0,
                            verbose=False, gui=False)

        return mv

    def synchronize(self):
        pass

    def addADTCommands(self):
        """
        Add to PMV some usefull ADT commands, and setup the conformation player.
        readDLG
        showDLGstates
        """

        from AutoDockTools.autoanalyzeCommands import ADGetDLG, StatesPlayerWidget, ShowAutoDockStates
        #        from AutoDockTools.autoanalyzeCommands import ADShowBindingSite
        self.mv.addCommand(ADGetDLG(), 'readDLG', None)
        # self.mv.addCommand(StatesPlayerWidget(),'playerDLG',None)
        self.mv.addCommand(ShowAutoDockStates(), 'showDLGstates', None)
        self.mv.userpref['Player GUI'] = {}
        self.mv.userpref['Player GUI']['value'] = 'Player'

    # general util function
    def createMesh(self, name, g, proxyCol=False, parent=None):
        """
        General function to create mesh from DejaVu.Geom.

        @type  name: string
        @param name: name of the host application
        @type  g: DejaVu.Geom
        @param g: the DejaVu geometry to convert in hostApp mesh
        @type  proxyCol: boolean
        @param proxyCol: if need special object when host didnt support color by vertex (ie C4D)
        @type  parent: hostApp object
        @param parent: the parent for the hostApp mesh
        """
        vertices = None
        faces = None
        if not hasattr(g, "getVertices"):
            # this os probably a extEl then just get vertices and faces
            vertices = g.vertices
            faces = g.faces
        else:
            vertices = g.getVertices()
            faces = g.getFaces()
        obj = self._createsNmesh(name, vertices, None, faces,
                                 proxyCol=proxyCol)
        #        print "_createsNmesh",obj
        self._addObjToGeom(obj, g)
        print ("mesh created", name, g, g.mesh, g.obj)
        self._addObjectToScene(self._getCurrentScene(), obj[0], parent=parent)
        return obj

    def getChainParentName(self, selection, mol):
        """
        Return the hostApp object masterParent at the chain level for a
        given MolKit selection.

        @type  selection: MolKit.AtomSet
        @param selection: the current selection
        @type  mol: MolKit.Protein
        @param mol: the selection's parent molecule

        @rtype:   hostApp object
        @return:  the masterparent object at the chain level or None
        """
        parent = None
        import time
        t1 = time.time()
        if len(selection) != len(mol.allAtoms):
            #            if self.host.find("t") != -1 :
            if isinstance(selection, AtomSet):
                chain = selection[0].parent.parent
            else:
                print (type(selection))
                return None
            #            else :
            #                chain=selection.findParentsOfType(Chain)[0]#way too slow
            parent = mol.geomContainer.masterGeom.chains_obj[chain.name]
            parent = self._getObject(parent)
        print (time.time() - t1)
        return parent

    def compareSel(self, currentSel, molSelDic):
        """
        Comapre the currentSel to the selection dictionary, return selname if retrieved.

        @type  currentSel: MolKit.AtomSet
        @param currentSel: the current selection
        @type  molSelDic: dictionary
        @param molSelDic: the dictionary of saved selection

        @rtype:   string
        @return:  the name of the selection in the dictionary if retrieved.
        """

        for selname in list(molSelDic.keys()):
            if currentSel[-1] == ';': currentSel = currentSel[0:-1]
            if currentSel == molSelDic[selname][3]: return selname
            if currentSel == molSelDic[selname]: return selname
        return None

    def getMolName(self, val, forupdate=False):
        #        print "get ",val
        selname = ""
        mname = val
        # print self.mv.iMol.keys()
        if mname in list(self.mv.selections.keys()):
            selname = mname
        #            print str(val),mname,selname
        else:  # it is the selecetionname
            for name in list(self.mv.selections.keys()):
                for sname in list(self.mv.selections[name].keys()):
                    if mname == sname:
                        selname = sname
                        mname = name
                    #        print mname
        mol = self.mv.getMolFromName(mname)
        #        print mol.name
        if forupdate:
            return selname, mol  # ?
        return mname, mol

    def sortName(self, array):
        stringselection = ""
        for element in array:
            if ":" in element:
                stringselection += element + ";"
            else:
                return element
        return stringselection

    def toStringSel(self, array):
        stringselection = ""
        #        print array
        for sel in array:
            for elem in sel:
                #                print elem,str(elem)
                stringselection += str(elem) + ":"
            stringselection = stringselection[:-1] + ";"
        #        print stringselection
        return stringselection

    def getSelectionLevel(self, mol, selString):
        # fix...problem if multiple chain...
        # R=mol.chains[0].residues
        if mol == None:
            sel = ''
        else:
            sel = mol.name
        selection = selString
        if selection == '' or selection == "" or len(selection) == 0:
            sel = mol.name
        elif selection.upper() == 'BACKBONE':
            sel = mol.name + ":::N,CA,C"
        elif selection.upper() == 'SIDECHAIN':
            sel = mol.name + ":::sidechain"
        elif selection.upper() in list(AtomElements.keys()):
            sel = mol.name + ':::' + selection
        elif selection.upper() in list(RasmolAmino.keys()):
            sel = mol.name + '::' + self.ResidueSelector.r_keyD[selection] + ':'
        elif selection.lower() in list(ResidueSetSelector.residueList.keys()):
            sel = mol.name + '::' + selection + ':'
        elif selection.split(':')[0] == mol.name:
            sel = selection
        elif selection.split(' ')[0].lower() == "chain":
            sel = mol.name + ':' + selection.split(' ')[1] + '::'
        elif selection == 'picked' and self.gui is not None:
            # need to get the current object selected in the doc
            # and parse their name to recognize the atom selection...do we define a picking level ? and some phantom object to be picked?
            CurrSel = self.helper.getCurrentSelection()
            astr = []
            for o in CurrSel:
                #                print o,self.parseObjectName(o)
                astr.append(self.parseObjectName(o, res=True))
            # ned to go from 3letter to 2letter
            sel = self.toStringSel(astr)

        #            print("parsed selection ",sel)
        #            print("from ",astr)
        # should be #B_MOL:CHAIN:RESIDUE:ATOMS
        # thus atoms =
        # sel=mol.name astr[3]
        elif selection[:5] == "(Mol:":
            if mol == None:
                sel = ''
            else:
                sel = mol.name
        else:
            sel = selection
        selection = self.mv.select(str(sel), negate=False, only=True, xor=False,
                                   log=0, intersect=False)
        if not isinstance(selection, Atom): selection = selection.findType(Atom)
        print("ok sel", str(sel), selString, len(selection), selection)  # ,selection
        return sel, selection

    def getSelectionCommand(self, selection, mol):
        """
        From the given currentSel and its parent molecule, return the selection name
        in the selection dictionary.

        @type  selection: MolKit.AtomSet
        @param selection: the current selection
        @type  mol: MolKit.Protein
        @param mol: the selection's parent molecule

        @rtype:   string
        @return:  the name of the selection in the dictionary if retrieved.
        """

        parent = None
        if hasattr(self.mv, "selections"):
            parent = self.compareSel('+selection+', self.mv.selections[mol.name])
        return parent

    def updateModel(self, event):
        """
        This is the callback function called everytime
        a PMV command affect the molecule data, ie deleteAtomSet.

        @type  event: VFevent
        @param event: the current event, ie DeleteAtomsEvent
        """

        if isinstance(event, AfterDeleteAtomsEvent):  # DeleteAtomsEvent):
            action = 'deleteAt'
            # when atom are deleted we have to redo the current representation and
            # selection
            atom_set = event.objects
            # mol = atom_set[0].getParentOfType(Protein)
            # need helperFunction to delete Objects
            for i, atms in enumerate(atom_set):
                nameo = "S" + "_" + atms.full_name()
                o = self._getObject(nameo)
                if o is not None:
                    #                    print nameo
                    self.helper.deleteObject(o)
                # and the ball/stick
                nameo = "B" + "_" + atms.full_name()
                o = self._getObject(nameo)
                if o is not None:
                    #                    print nameo
                    self.helper.deleteObject(o)
                # and the bonds...and other geom?
            mol = atom_set[0].top  # getParentOfType(Protein)
            self.mv.buildBondsByDistance(mol, log=0)
        elif isinstance(event, BeforeDeleteMoleculesEvent):
            action = 'deletMol'
            #            print action,dir(event)
            mols = event.arg
            for mol in mols:
                #                print "delete",mol.name
                self.delMolDic(mol.name)
                self.delGeomMol(mol)
            if self.gui is not None:
                # need to update molmenu
                self.gui.resetPMenu(self.gui.COMB_BOX["mol"])
                self.gui.restoreMolMenu()

    # the main function, call every time an a geom event is dispatch
    def updateGeom(self, event):
        """
        This the main core of ePMV, this is the callback function called everytime
        a PMV command affect a geometry.

        @type  event: VFevent
        @param event: the current event, ie EditGeomsEvent
        """

        if isinstance(event, AddGeomsEvent):
            action = 'add'
        elif isinstance(event, DeleteGeomsEvent):
            action = 'delete'
        elif isinstance(event, EditGeomsEvent):
            action = 'edit'
        else:
            import warnings
            warnings.warn('Bad event %s for epmvAdaptor.updateGeom' % event)
            return
        nodes, options = event.objects
        if event.arg == 'iso':
            self._isoSurface(nodes, options)
            return
        mol, atms = self.mv.getNodesByMolecule(nodes, Atom)
        #################GEOMS EVENT############################################
        if event.arg == 'lines' and action == 'edit':
            self._editLines(mol, atms)
        elif event.arg == 'cpk' and action == 'edit' and not self.useLog:
            self._editCPK(mol, atms, options)
        elif event.arg == 'bs' and action == 'edit' and not self.useLog:
            self._editBS(mol, atms, options)
        elif event.arg == 'trace' and action == 'edit' and not self.useLog:
            print("displayTrace not supported Yet")
            # displayTrace should use a linear spline extruded like _ribbon command
        elif event.arg[0:4] == 'msms' and action == 'edit' and not self.useLog:
            # there is 2 different msms event : compute msms_c and display msms_ds
            if event.arg == "msms_c":  # ok compute
                self._computeMSMS(mol, atms, options)
            elif event.arg == "msms_ds":  # ok display
                self._displayMSMS(mol, atms, options)
        elif event.arg[:2] == 'SS' and action == 'edit' and not self.useLog:
            # if event.arg == "SSextrude":
            #    self._SecondaryStructure(mol,atms,options,extrude=True)
            if event.arg == "SSdisplay":
                self._SecondaryStructure(mol, atms, options)
            if event.arg == "SSdisplayU":
                self._SecondaryStructure(mol, atms, options, uniq=True)

        # the bead riibbon ?
        # ('bead', [nodes,[params,redraw]],setOn=setOn, setOff=setOff)
        elif event.arg == 'bead' and action == 'edit':
            self._beadedRibbons(mol, atms, options[0])
        elif event.arg == 'beadU' and action == 'edit':
            self._beadedRibbons(mol, atms, options[0], uniq=True)
        # self.beadedRibbons("1crn", redraw=0, log=1)
        #################COLOR EVENT############################################
        elif event.arg[0:5] == "color":  # color Commands
            # in this case liste of geoms correspond to the first options
            # and the type of function is the last options
            self._color(mol, atms, options)
        elif event.arg == 'struts' and action == 'edit':
            self._struts(mol, atms, options[0])  # nodes, params

    def delMolDic(self, mname):
        if mname in self.mv.selections:
            del self.mv.selections[mname]
        if mname in self.mv.iMolData:
            del self.mv.iMolData[mname]
        if mname in self.mv.molDispl:
            del self.mv.molDispl[mname]
        if mname in self.mv.MolSelection:
            del self.mv.MolSelection[mname]
        #        print self.mv.selections

    def delGeomMol(self, mol):
        master = mol.geomContainer.masterGeom.obj
        self.helper.deleteChildrens(master)
        for g in mol.geomContainer.geoms:
            if hasattr(g, 'obj'):
                del g.obj
            if hasattr(g, 'mesh'):
                del g.mesh

    def _addMolecule(self, molname):
        """
        Initialise a molecule. ie prepare the specific dictionary for this molecule.

        @type  molname: str
        @param molname: the molecule name
        """
        if molname not in list(self.mv.molDispl.keys()):
            self.mv.molDispl[molname] = {}
            for k in ["cpk", "bs", "ss", "bead", "loft", "arm", "spline",
                      "surf", "cms", "meta", "points", "lines", "cgeom"]:
                self.mv.molDispl[molname][k] = False
            self.mv.molDispl[molname]["col"] = None
        if molname not in list(self.mv.MolSelection.keys()):
            self.mv.MolSelection[molname] = {}
        if molname not in list(self.mv.selections.keys()):
            self.mv.selections[molname] = {}
        if molname not in list(self.mv.iMolData.keys()):
            self.mv.iMolData[molname] = []
        molinDic = False
        for k in self.molDictionary:
            if molname == self.molDictionary[k][0]:
                molinDic = True
        if not molinDic:
            self.molDictionary[self.hmol] = [molname, self.mv.Mols.name.index(molname)]
            self.hmol += 1

    def _deleteMolecule(self, mol):
        if mol.name in self.mv.Mols.name:
            # need to first delete the geom and the associates dictionary
            # note the mesh are still in the memory ....
            self.delMolDic(mol.name)
            try:
                self.delGeomMol(mol)
            except:
                print("oups")
            # then delete the mol
            self.mv.deleteMol(mol, log=0)
            # del cam and light
            # need to update  self.molDictionary[molname]
            self.molDictionary = {}
            for i, mol in enumerate(self.mv.Mols):
                mindice, mvindice = self.getIndiceMol(mol.name)
                self.molDictionary[mindice] = [mol.name, self.mv.Mols.name.index(mol.name)]

    def _toggleUpdateSphere(self, atms, display, needRedo, i, N, prefix, opts=None):
        """
        Handle the visibility and the update (pos) of each atom's Sphere geometry.
        i and N arg are used for progress bar purpose.

        @type  atms: MolKit.Atom
        @param atms: the atom to handle
        @type  display: boolean
        @param display: visibility option
        @type  needRedo: boolean
        @param needRedo: do we need to update
        @type  i: int
        @param i: the atom indice
        @type  N: int
        @param N: the total number of atoms
        @type  prefix: str
        @param prefix: cpk or ball sphere geometry, ie "S" or "B"
        """
        # TODO, fix problem with Heteratom that can have the same fullname
        nameo = self.atomNameRule(atms, prefix)
        #        print nameo
        # prefix+"_"+atms.full_name().replace("'","b")+"n"+str(atms.number)
        o = self._getObject(nameo)
        if o != None:
            self._toggleDisplay(o, display)
            if display and not self.use_instances:
                if prefix == "B":
                    quality = opts[4]
                    cpkRad = opts[2]
                    scale = opts[3]
                else:
                    quality = opts[4]
                    cpkRad = opts[3]
                    scale = opts[2]
                name = atms.element
                if atms.element not in self.AtmRadi:
                    name = "A"
                factor = float(cpkRad) + float(self.AtmRadi[name]) * float(scale)
                self.helper.updateSphereMesh(o, basemesh="mesh_basesphere",
                                             scale=factor)
            if needRedo:
                self._updateSphereObj(o, atms.coords)
                if self.use_progressBar and (i % 20) == 0:
                    progress = float(i) / N
                    self._progressBar(progress, 'update Spheres')

    def _updateOneBond(self, bds, **kw):
        atm1 = bds.atom1
        atm2 = bds.atom2
        if not self.bicyl:
            c0 = numpy.array(atm1.coords)
            c1 = numpy.array(atm2.coords)
            n1 = atm1.full_name().split(":")
            name = self.bondNameRule(atm1, atm2, "T")[0]
            self._updateTubeObj(name, c0, c1)
        else:
            c0 = numpy.array(atm1.coords)
            c1 = numpy.array(atm2.coords)
            vect = c1 - c0
            name1, name2 = self.bondNameRule(atm1, atm2, "T")
            med = numpy.array(c0 + (vect / 2.))
            self._updateTubeObj(name1, c0, med)
            self._updateTubeObj(name2, numpy.array(c0 + (vect / 2.)), c1)

    def _toggleUpdateStick(self, bds, display, needRedo, i, N, molname, opts=None):
        """
        Handle the visibility and the update (pos) of each atom's bonds cylinder geometry.
        i and N arg are used for progress bar purpose.

        @type  bds: MolKit.Bonds
        @param bds: the bonds to handle
        @type  display: boolean
        @param display: visibility option
        @type  needRedo: boolean
        @param needRedo: do we need to update
        @type  i: int
        @param i: the atom indice
        @type  N: int
        @param N: the total number of atoms
        @type  molname: str
        @param molname: the name of the parent molecule.
        """
        atm1 = bds.atom1
        atm2 = bds.atom2
        if not self.bicyl:
            c0 = numpy.array(atm1.coords)
            c1 = numpy.array(atm2.coords)
            n1 = atm1.full_name().split(":")
            name = self.bondNameRule(atm1, atm2, "T")[0]
            #            name="T_"+atm1.name.replace("'","b")+str(atm1.number)+"_"+atm2.name.replace("'","b")+str(atm2.number)
            #            name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
            #            name="T_"+molname+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
            #            name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
            o = self._getObject(name)
            if o != None:
                if needRedo:
                    self._updateTubeObj(o, c0, c1)
                self._toggleDisplay(o, display=display)
        else:
            c0 = numpy.array(atm1.coords)
            c1 = numpy.array(atm2.coords)
            vect = c1 - c0

            name1, name2 = self.bondNameRule(atm1, atm2, "T")
            #            print name1,c0,c1,vect
            #            n1=atm1.full_name().split(":")
            #            n2=atm2.full_name().split(":")
            #            name1="T_"+molname+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
            #            name2="T_"+molname+"_"+n2[1]+"_"+util.changeR(n2[2])+"_"+n2[3]+"_"+atm1.name
            #            name1 = name1.replace("'","b")
            #            name2 = name2.replace("'","b")
            o = self._getObject(name1)
            if o != None:
                if needRedo:
                    med = numpy.array(c0 + (vect / 2.))
                    self._updateTubeObj(o, c0, med)
                if not self.use_instances:
                    cradius = opts[5]
                    quality = opts[6]
                    self.helper.updateTubeMesh(o, basemesh="mesh_baseCyl",
                                               cradius=cradius, quality=quality)
                self._toggleDisplay(o, display=display)
            o = self._getObject(name2)
            if o != None:
                if needRedo:
                    self._updateTubeObj(o, numpy.array(c0 + (vect / 2.)), c1)
                if not self.use_instances:
                    cradius = opts[5]
                    quality = opts[6]
                    self.helper.updateTubeMesh(o, basemesh="mesh_baseCyl",
                                               cradius=cradius, quality=quality)
                self._toggleDisplay(o, display=display)
        if self.use_progressBar and (i % 20) == 0:
            progress = float(i) / N
            self._progressBar(progress, 'update sticks')

    def _editCPK(self, mol, atms, opts):
        """
        Callback for displayCPK commands. Create and update the cpk geometries

        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  opts: list
        @param opts: the list of option used for the command (only, negate, scaleFactor,
        cpkRad, quality, byproperty, propertyName, propertyLevel, redraw)
        """

        sc = self._getCurrentScene()
        display = not opts[1]
        print ("EditCPK options", opts)
        needRedo = opts[8]
        print("redo", needRedo)
        options = self.mv.displayCPK.lastUsedValues["default"]
        if "redraw" in options: needRedo = options["redraw"]
        print ("redo", needRedo)
        ##NB do we want to handle multiple mol at once?
        mol = mol[0]
        g = mol.geomContainer.geoms['cpk']
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        sel = atms[0]
        if not hasattr(g, "obj") and display:
            name = mol.name + "_cpk"
            print ("base sphere create")
            mesh = self._createBaseSphere(name=mol.name + "_b_cpk", quality=opts[4], cpkRad=opts[3],
                                          scale=opts[2], parent=root)
            print ("base sphere created", mesh)
            ob = self._instancesAtomsSphere(name, sel, mesh, sc, scale=opts[2],
                                            R=opts[3], Res=opts[4], join=self.joins,
                                            geom=g, pb=self.use_progressBar)
            self._addObjToGeom([ob, mesh], g)
        if hasattr(g, "obj"):
            # update number of spheres instance
            if len(sel) != len(g.obj):
                name = mol.name + "_cpk"
                print ("create all the sphere instances")
                ob = self._instancesAtomsSphere(name, sel, g.mesh, sc, scale=opts[2],
                                                R=opts[3], Res=opts[4], join=self.joins,
                                                geom=g, pb=self.use_progressBar)
                g.obj = ob
            if display:
                self._updateSphereMesh(g, quality=opts[4], cpkRad=opts[3], scale=opts[2], prefix="S")
            # update the instanceObject

            atoms = sel
            if self.use_progressBar: self._resetProgressBar(len(atoms))
            # can we reaplce the map/lambda by [[]]?
            # toggle only the parent
            for c in mol.chains:
                parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name + "_cpk"])
                self._toggleDisplay(parent, display)
                # if needRedo and display :
                #    for x in enumerate(atoms):
                #        nameo = self.atomNameRule(x,"S")
                #        o=self._getObject(nameo)
                #        self._updateSphereObj(o,x.coords)
            #            [self._toggleUpdateSphere(x[1],display,needRedo,x[0],
            #                                        len(atoms),"S",opts=opts) for x in enumerate(atoms)]

    def _editBS(self, mol, atms, opts):
        """
        Callback for displayStickandBalls commands. Create and update the sticks
        and balls geometries

        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  opts: list
        @param opts: the list of option used for the command (only, negate, bRad,
        bScale, bquality, cradius, cquality, sticksBallsLicorice, redraw)
        """
        #        print opts
        sc = self._getCurrentScene()
        display = not opts[1]
        needRedo = opts[-1]
        options = self.mv.displaySticksAndBalls.lastUsedValues["default"]
        if "redraw" in options: needRedo = options["redraw"]

        # NB do we want to handle multiple mol at once?
        mol = mol[0]
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        sel = atms[0]
        # if not hasattr(g,"obj") and display:
        doSphere = False
        doStick = False
        gb = mol.geomContainer.geoms['balls']
        gs = mol.geomContainer.geoms['sticks']
        mesh = None
        if not hasattr(gb, "obj") and not hasattr(gs, "obj"):
            mol.allAtoms.ballRad = opts[2]
            mol.allAtoms.ballScale = opts[3]
            mol.allAtoms.cRad = opts[5]
            for atm in mol.allAtoms:
                atm.colors['sticks'] = (1.0, 1.0, 1.0)
                atm.opacities['sticks'] = 1.0
                atm.colors['balls'] = (1.0, 1.0, 1.0)
                atm.opacities['balls'] = 1.0
            if opts[7] != 'Sticks only':  # no balls
                if not hasattr(gb, "obj") and display:
                    doSphere = True
                    mesh = self._createBaseSphere(name=mol.name + "_b_balls", quality=opts[4],
                                                  cpkRad=opts[2], scale=opts[3],
                                                  radius=opts[2], parent=root)
                #                    ob=self._instancesAtomsSphere(mol.name+"_balls",sel,mesh,sc,
                #                                                  scale=opts[3],R=opts[2],
                #                                                  join=self.joins,geom=gb,
                #                                                  pb=self.use_progressBar)
                #                    self._addObjToGeom([ob,mesh],gb)
                #                    gb.mesh=mesh
            if not hasattr(gs, "obj") and display:
                set = mol.geomContainer.atoms["sticks"]
                doStick = True
            #                stick=self._Tube(set,sel,gs.getVertices(),gs.getFaces(),sc, None,
            #                                 res=15, size=opts[5], sc=1.,join=0,bicyl=self.bicyl,
            #                                 hiera =self.useTree,pb=self.use_progressBar)
            #                gs.obj = stick[0]
            #                gs.mesh =stick[1]
            #                print ("instance ",gs.mesh)
            #                self._addObjToGeom(stick,gs)
            ob, stick = self._doBS(sel, doSphere, doStick, mol.name + "_b_balls", gb=gb,
                                   # sticks options
                                   res=15, size=opts[5], sc=1., bicyl=self.bicyl,
                                   hiera=self.useTree,
                                   # balls options
                                   iMe=mesh, scale=opts[3], R=opts[2], Res=opts[4],
                                   join=0, pb=self.use_progressBar
                                   )
            self._addObjToGeom([ob, mesh], gb)
            #            gb.obj = ob
            #            gb.mesh = mesh
            gs.obj = stick[0]
            gs.mesh = stick[1]
            # self._addObjToGeom(stick,gs)
        upSphere = False
        upStick = False
        # update mesh
        if hasattr(gb, "obj"):
            # if needRedo :
            if len(sel) != len(gb.obj):
                name = mol.name + "_balls"
                upSphere = True
                upStick = True
            self._updateSphereMesh(gb, quality=opts[4], cpkRad=opts[2],
                                   scale=opts[3], radius=opts[2], prefix="B")
        if hasattr(gs, "obj"):
            #            if (len(gs.getVertices()) != len(gs.obj)):
            #            upStick = True
            self._updateTubeMesh(gs, cradius=opts[5], quality=opts[6])
        # update instance
        name = mol.name + "_balls"
        ob, stick = self._doBS(sel, upSphere, upStick, mol.name + "_b_balls", gb=gb, gs=gs,
                               # sticks options
                               res=15, size=opts[5], sc=1., bicyl=self.bicyl,
                               hiera=self.useTree,
                               # balls options
                               iMe=gb.mesh, scale=opts[3], R=opts[2], Res=opts[4],
                               join=0, pb=self.use_progressBar)
        gb.obj = ob
        gs.obj = stick[0]
        # update display
        if self.use_progressBar: self._resetProgressBar(len(atoms))
        if opts[7] == 'Sticks only':
            display = False
        else:
            display = display
        if len(sel) <= 0:
            return
        for c in mol.chains:
            parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name + "_balls"])
            self._toggleDisplay(parent, display)
            # for i,at in enumerate(sel):
            #    bonds= at.bonds
            #    self._toggleUpdateSphere(at,display, needRedo,i,
            #                                len(sel),"B",opts=opts)
            #    for j,bond in enumerate(bonds):
            #        self._toggleUpdateStick(bond,display,needRedo,j,len(bonds),
            #                               mol.name,opts=opts)

        #        if hasattr(gb,"obj"):
        #            #if needRedo :
        #            if len(sel)!= len(gb.obj):
        #                name=mol.name+"_balls"
        #                ob=self._instancesAtomsSphere(name,sel,gb.mesh,sc,scale=opts[2],
        #                                          R=opts[3],Res=opts[4],join=self.joins,
        #                                          geom=gb,pb=self.use_progressBar)
        #                gb.obj = ob
        #            self._updateSphereMesh(gb,quality=opts[4],cpkRad=opts[2],
        #                                           scale=opts[3],radius=opts[2])
        #            atoms=sel
        #            if self.use_progressBar : self._resetProgressBar(len(atoms))
        #            if opts[7] =='Sticks only' :
        #                display = False
        #            else :  display = display
        #            [self._toggleUpdateSphere(x[1],display, needRedo,x[0],
        #                                        len(atoms),"B") for x in enumerate(atoms)]
        ##            map(lambda x,display=display,needRedo=needRedo,N=len(atoms):
        ##                        self._toggleUpdateSphere(x[1],display,needRedo,x[0],N,"B"),
        ##                        enumerate(atoms))
        #
        #        if hasattr(gs,"obj"):
        #            #first update geom
        #            #_Tube again?
        #            print ("gs ",len(gs.getVertices()) , len(gs.obj))
        #            if (len(gs.getVertices()) != len(gs.obj)):
        #                set = mol.geomContainer.atoms["sticks"]
        #                stick,inst=self._Tube(set,sel,gs.getVertices(),gs.getFaces(),sc, None,
        #                                 res=15, size=opts[5], sc=1.,join=0,bicyl=self.bicyl,
        #                                 hiera =self.useTree,pb=self.use_progressBar,g=gs)
        #                gs.obj = stick
        #            self._updateTubeMesh(gs,cradius=opts[5],quality=opts[6])
        #            atoms=sel
        #            #set = mol.geomContainer.atoms["sticks"]
        #            bonds, atnobnd = atoms.bonds
        #            #print len(atoms)
        #            #for o in gs.obj:util.toggleDisplay(o,display=False)
        #            if len(atoms) > 0 :
        #                if self.use_progressBar : self._resetProgressBar(len(bonds))
        #                [self._toggleUpdateStick(x[1],display,needRedo,x[0],len(bonds),
        #                                           mol.name) for x in enumerate(bonds)]
        #                map(lambda x,display=display,needRedo=needRedo,N=len(bonds),molname=mol.name:
        #                        self._toggleUpdateStick(x[1],display,needRedo,x[0],N,molname),
        #                        enumerate(bonds))

    def _struts(self, mol, atms, options):
        thresh = options['distCutoff']
        distance = options['distCutoff2']
        # need to make instance of cylinder or other geometries for each struts
        pass

    def _SecondaryStructure(self, mol, atms, options, extrude=False, uniq=False):
        """
        Callback for display/extrudeSecondaryStructrure commands. Create and update
        the mesh polygons for representing the secondary structure


        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command (only, negate, bRad,
        bScale, bquality, cradius, cquality, sticksBallsLicorice, redraw)
        @type  extrude: boolean
        @param extrude: type of command : extrude or display
        """
        chname = ['Z', 'Y', 'X', 'W', 'V', 'U', 'T']
        proxy = self.colorProxyObject
        join = self.join_ss
        self.colorProxyObject = False
        sc = self._getCurrentScene()
        mol = mol[0]
        sel = atms[0]
        #        print mol, sel, len(mol.allAtoms) != len(sel)
        selection = len(mol.allAtoms) != len(sel)
        chn = sel[0].getParentOfType(Chain)
        #        print chn
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        display = not options[1]
        i = 0
        if extrude:
            display = options[9]
        # check the ss
        # print ("chn",hasattr(chn,"secondarystructureset"))
        if not hasattr(chn, "secondarystructureset"):
            return
        for ch in mol.chains:
            #            print ch.name
            listeObj = []
            if selection and ch is chn:
                ch = chn
            #                print chn.name
            if not hasattr(ch, "secondarystructureset"):
                return
            parent = self._getObject(chobj[ch.name + "_ss"])
            if uniq:
                name = "SS" + ch.id
                g = mol.geomContainer.geoms[name]
                obj = self._getObject(mol.name + "_" + ch.name + "_" + name)
                if (not hasattr(g, "obj") and obj is None) and display:
                    obj = self.createMesh(mol.name + "_" + ch.name + "_" + name, g, parent=parent)
                    # self.mv.colorBySecondaryStructure(mol.name,[name])#problem of material...
                    listeObj.append(obj[0])
                elif hasattr(g, "obj") or obj is not None:
                    if not hasattr(g, "obj"):
                        self._addObjToGeom(obj, g)  # ex.obj = obj
                    self._toggleDisplay(obj, display)
            else:
                for elem in ch.secondarystructureset:
                    # get the geom or the extruder ?
                    if hasattr(elem, "exElt"):
                        ex = elem.exElt
                    else:
                        continue
                    name = elem.name
                    #                print (ex,display,hasattr(ex,"obj"))
                    obj = self._getObject(mol.name + "_" + ch.name + "_" + name)
                    g = mol.geomContainer.geoms[ex.ssElt.name + ch.name]
                    #                print (obj,hasattr(ex,"obj"))
                    if (not hasattr(ex, "obj") and obj is None) and display:
                        #                    print mol.name+"_"+ch.name+"_"+name
                        parent = self._getObject(chobj[ch.name + "_ss"])
                        obj = self.createMesh(mol.name + "_" + ch.name + "_" + name, ex, parent=parent)
                        listeObj.append(obj[0])
                        if not hasattr(ex, "mesh"):
                            #    self._addObjToGeom(obj,ex)#.obj = obj
                            ex.mesh = obj[1]
                        self._addObjToGeom(obj, g)
                        elem.exElt.name = name
                        # change the material color to ss
                        for key in list(SecondaryStructureType.keys()):
                            if key in name:
                                color = SecondaryStructureType[key]
                                break
                        matname = "mat_" + self.helper.getName(ex.obj)
                        mat = self.helper.getMaterial(matname)
                        if mat is None:
                            pass
                            # mat = self.helper.addMaterial(matname,color)
                            # self.helper.assignMaterial(self._getObject(obj[1]),mat)
                        else:
                            self.helper.colorMaterial(matname, color)
                        if ch.ribbonType() == 'NA':
                            # name = mol.name+"_"+c.name+"_lader"
                            # make the ladder
                            if hasattr(ex, "obj"):
                                parent = ex.obj
                            laders = self.NAlader("rib", mol, ch, parent=parent, bilader=False)[0]
                            g.children[0].obj = laders

                    elif hasattr(ex, "obj") or obj is not None:
                        #                    print ("toggle",display,obj)
                        if not hasattr(ex, "obj"):
                            self._addObjToGeom(obj, ex)  # ex.obj = obj
                        if not hasattr(ex, "mesh"):
                            ex.mesh = self.helper.getMeshFrom(obj)
                        if not hasattr(g, "obj"):
                            self._addObjToGeom(obj, g)  # ex.obj = obj
                        if not hasattr(g, "mesh"):
                            g.mesh = self.helper.getMeshFrom(obj)

                            # self._updateMesh(ex)#?
                            #                    print "d",ex.obj,display
                        self._toggleDisplay(obj, display)
                        if ch.ribbonType() == 'NA':
                            o = self._getObject("rib" + mol.name + ch.name + "_lader")
                            # self._toggleDisplay(o,display)
                            #                print "after",ex,display,hasattr(ex,"obj")
                    listeObj.append(obj)
                # join ?
                if join:
                    self.helper.JoinsObjects(listeObj)
                    # bindToGeom ?
            if selection:
                break
            if self.use_progressBar and (i % 20) == 0:
                progress = float(i) / 100  # len(self.mv.sets.keys())
                self._progressBar(progress, 'add SS to scene')
                i += 1
        self.colorProxyObject = proxy

    def _beadedRibbons(self, mol, atms, params, uniq=False):
        """
        Callback for display/extrudeSecondaryStructrure commands. Create and update
        the mesh polygons for representing the secondary structure


        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command alos found by mol.beadedRibbonParams:
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
             \nsheetArrowHeadLength --- length of sheet's arrow (default 8)
        """
        # display option ?
        # DEPRECATED and not used....
        chname = ['Z', 'Y', 'X', 'W', 'V', 'U', 'T']
        proxy = self.colorProxyObject
        self.colorProxyObject = False
        sc = self._getCurrentScene()
        mol = mol[0]
        sel = atms[0]
        #        print mol, sel, len(mol.allAtoms) != len(sel)
        selection = len(mol.allAtoms) != len(sel)
        chn = sel[0].getParentOfType(Chain)
        #        print chn
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        # display = not options[1]
        i = 0
        # if extrude :display = options[9]
        # check the ss
        if not hasattr(chn, "secondarystructureset"):
            return
        # check also uniq_ss
        for ch in mol.chains:
            #            print ch.name
            if selection and ch is chn:
                ch = chn
            #                print chn.name
            parent = self._getObject(chobj[ch.name + "_ss"])
            # should create a new parent beadedribbon
            beadparent = self.helper.newEmpty(mol.name + ch.name + "_bead")
            self.helper.addObjectToScene(sc, beadparent, parent=parent)
            for SS in ch.secondarystructureset:  # for i, SS in enumerate(chain.secondarystructureset)
                # get the geom or the extruder ?
                name = SS.name
                type = SS.structureType
                lgeoms = []
                lcolors = []
                # need mv to findGeomFromName
                # depending on Thickness number of geometry will change...
                if type == "Strand":
                    elem = ["_edge1", "_edge2", "_faces", "_faces2", "_sides"]
                    colors = [params['sheetBeadColor1'], params['sheetBeadColor2'],
                              params['sheetColor1'], params['sheetColor2'], col.greenyellow]
                elif type == "Helix":
                    elem = ["_edge1", "_edge2", "A_faces", "_faces2", "_sides"]
                    colors = [params['helixBeadColor1'], params['helixBeadColor2'],
                              params['helixColor1'], params['helixColor2'], col.greenyellow]
                elif type == "Coil" or type == 'Turn':
                    elem = [""]
                    colors = [params['coilColor']]
                for i, e in enumerate(elem):
                    fullname = '%s|beadedRibbon|chain%s|%s' % (
                        mol.name, ch.id, SS.name + e)
                    geom = self.mv.FindObjectByName_noGui(mol.geomContainer.masterGeom, fullname)
                    #                    print fullname,"found",geom
                    lgeoms.append(geom)
                    lcolors.append(colors[i])
                # get beadedGeom
                for i, g in enumerate(lgeoms):
                    if not hasattr(g, "obj"):
                        self.createMesh(mol.name + "_" + ch.name + "_" + g.name, g, parent=beadparent)
                        # color it
                        matname = "mat_" + self.helper.getName(g.obj)
                        self.helper.colorMaterial(matname, lcolors[i])
                    #                    if ch.ribbonType()=='NA':
                    #                        #name = mol.name+"_"+c.name+"_lader"
                    #                        #make the ladder
                    #                        g = mol.geomContainer.geoms[ex.ssElt.name+ch.name]
                    #                        if hasattr(ex,"obj") :
                    #                            parent = ex.obj
                    #                        laders=self.NAlader("rib",mol,ch,parent = parent,bilader=False)[0]
                    #                        g.children[0].obj = laders
                    elif hasattr(g, "obj"):
                        #                        pass
                        self._updateMesh(g)
                        matname = "mat_" + self.helper.getName(g.obj)
                        self.helper.colorMaterial(matname, lcolors[i])
                    #                        self._toggleDisplay(g.obj,display)
                    #                        if ch.ribbonType()=='NA':FindObjectByName_noGui
                    #                            o=self._getObject("rib"+mol.name+"_"+ch.name+"_lader")
                    #                            #self._toggleDisplay(o,display)

                    if selection:
                        break
                    if self.use_progressBar and (i % 20) == 0:
                        progress = float(i) / 100  # len(self.mv.sets.keys())
                        self._progressBar(progress, 'add SS to scene')
                        i += 1
                        # self.colorProxyObject = proxy

    def _computeMSMS(self, mol, atms, options):
        """
        Callback for computation of MSMS surface. Create and update
        the mesh polygons for representing the MSMS surface


        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command; options order :
        surfName, pRadius, density,perMol, display, hdset, hdensity
        """

        name = options[0]
        mol = mol[0]
        root = mol.geomContainer.masterGeom.obj
        # chobj = mol.geomContainer.masterGeom.chains_obj
        sel = atms[0]
        parent = self.getChainParentName(sel, mol)
        if parent == None: parent = root
        g = mol.geomContainer.geoms[name]
        if not hasattr(g, "mol"):
            g.mol = mol
        if hasattr(g, "obj"):
            self._updateMesh(g)
        else:
            self.createMesh(name, g, parent=parent, proxyCol=True)
        if options[4]:
            self._toggleDisplay(g.obj, display=options[4])

    def _displayMSMS(self, mol, atms, options):
        """
        Callback for displayMSMS commands. display/undisplay
        the mesh polygons representing the MSMS surface

        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command; options order :
        surfName, pRadius, density,perMol, display, hdset, hdensity
        """
        # options order : surfName(names), negate, only, nbVert
        # this function only toggle the display of the MSMS polygon
        name = options[0][0]  # surfName(names) is a list...
        display = not options[1]
        g = mol[0].geomContainer.geoms[name]
        if hasattr(g, "obj"):
            self._toggleDisplay(g.obj, display=display)

    def _updateArmature(self, name, atomset, coords=None, root=None, scn=None):
        pass

    def _armature(self, name, atomset, coords=None, root=None, scn=None):
        pass

    def _colorStick(self, bds, i, atoms, N, fType, p, mol):
        """
        Handle the coloring of one bonds stick geometry.
        i and N arg are used for progress bar purpose.

        @type  bds: MolKit.Bonds
        @param bds: the bonds to color
        @type i: int
        @param i: the bond indice
        @type  atoms: MolKit.AtomSet
        @param atoms: the list of atoms
        @type  N: int
        @param N: the total number of bonds
        @type  fType: str
        @param fType: the colorCommand type
        @type  p: Object
        @param p: the parent object
        @type  mol: MolKit.Protein
        @param mol: the molecule parent
        """
        atm1 = bds.atom1
        atm2 = bds.atom2
        if atm1 in atoms or atm2 in atoms:
            vcolors = [atm1.colors["sticks"], atm2.colors["sticks"]]
            if not self.bicyl:
                name = self.bondNameRule(atm1, atm2, "T")[0]
                # name="T_"+atm1.name.replace("'","b")+str(atm1.number)+"_"+atm2.name.replace("'","b")+str(atm2.number)
                # n1=atm1.full_name().split(":").replace("'","b")
                # name="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name.replace("'","b")
                #                name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
                o = self._getObject(name)
                if o != None:
                    self._checkChangeMaterial(o, fType,
                                              atom=atm1, parent=p, color=vcolors[0])
            else:
                #                n1=atm1.full_name().split(":")
                #                n2=atm2.full_name().split(":")
                name1, name2 = self.bondNameRule(atm1, atm2, "T")
                #                name1="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
                #                name2="T_"+mol.name+"_"+n2[1]+"_"+util.changeR(n2[2])+"_"+n2[3]+"_"+atm1.name
                #                name1 = name1.replace("'","b")
                #                name2 = name2.replace("'","b")
                o = self._getObject(name1)
                if o != None:
                    self._checkChangeMaterial(o, fType,
                                              atom=atm1, parent=p, color=vcolors[0])
                o = self._getObject(name2)
                if o != None:
                    self._checkChangeMaterial(o, fType,
                                              atom=atm2, parent=p, color=vcolors[1])
        if self.use_progressBar and (i % 20) == 0:
            progress = float(i) / N
            self._progressBar(progress, 'color Sticks')

    def _colorSphere(self, atm, i, sel, prefix, p, fType, geom, colors=None):
        """
        Handle the coloring of one atom sphere geometry.
        i and N arg are used for progress bar purpose.

        @type  atm: MolKit.Atom
        @param atm: the atom to color
        @type i: int
        @param i: the atom indice
        @type  sel: MolKit.AtomSet
        @param sel: the list of atoms
        @type  prefix: str
        @param prefix: cpk or ball sphere geometry, ie "S" or "B"
        @type  p: Object
        @param p: the parent object
        @type  fType: str
        @param fType: the colorCommand type
        @type  geom: str
        @param geom: the parent geometry ie cpk or balls
        """
        name = self.atomNameRule(atm, prefix)
        # prefix+"_"+atm.full_name().replace("'","b")+"n"+str(atm.number)
        o = self._getObject(name)
        print (o, name, prefix)
        if colors is None:
            vcolors = [atm.colors[geom], ]
        else:
            vcolors = [colors]
        if o != None:
            self._checkChangeMaterial(o, fType, atom=atm, parent=p, color=vcolors[0])
            if self.use_progressBar and (i % 20) == 0:
                progress = float(i) / len(sel)
                self._progressBar(progress, 'color Spheres')

    def retrieveAtColorFrom(self, atom, selection, colors, geom):
        if colors is not None:
            return colors[selection.index(atom)]
        else:
            return atom.colors[geom]

    def _colorLadder(self, mol, chain, fType, colors, geom="secondarystructure",
                     bilader=False, name="rib", sel=None):
        if sel is not None:
            residues = sel.parent
            total_res = len(residues)
        else:
            residues = chain.residues
            total_res = len(residues)
        color = None
        # name = "rib"#depend if ribbon or beaded or loft...
        for i in range(total_res):
            # need two point per residues P->C6 / C6->N3 C T
            # need two point per residues P->C8 / C8->N1 ['A', 'G', 'DA', 'DG']
            NA_type = residues[i].type.strip()
            try:
                # at1 = residues[i].atoms.objectsFromString('P')[0]
                at1 = residues[i].atoms.objectsFromString("O5'")[0]
            except:
                continue
                # at1 = residues[i].atoms[0]#take first atoms # or last ?
            if NA_type in ['A', 'G', 'DA', 'DG']:
                at2 = residues[i].atoms.objectsFromString('C8')[0]
                at3 = residues[i].atoms.objectsFromString('N1')[0]
            else:
                at2 = residues[i].atoms.objectsFromString('C6')[0]
                at3 = residues[i].atoms.objectsFromString('N3')[0]
            self._colorSphere(at1, i, total_res, "L", None, fType, geom,
                              colors=self.retrieveAtColorFrom(at1, sel, colors, geom))
            #            sph=self.helper.getObject(name+at1.full_name())
            #            if sph is not None :
            #                vcolors = [at1.colors[geom],]
            #                self._checkChangeMaterial(sph,fType,atom=at1,color=vcolors[0])
            if bilader:
                self._colorSphere(at2, i, total_res, "L", None, fType, geom,
                                  colors=self.retrieveAtColorFrom(at2, sel, colors, geom))
            #                sph=self.helper.getObject(name+at2.full_name())
            #                if sph is not None :
            #                    vcolors = [at2.colors[geom],]
            #                    self._checkChangeMaterial(sph,fType,atom=at2,color=vcolors[0])
            self._colorSphere(at3, i, total_res, "L", None, fType, geom,
                              colors=self.retrieveAtColorFrom(at3, sel, colors, geom))
            #            sph=self.helper.getObject(name+at3.full_name())
            #            if sph is not None :
            #                vcolors = [at2.colors[geom],]
            #                self._checkChangeMaterial(sph,fType,atom=at2,color=vcolors[0])
            if bilader:
                stick = self.helper.getObject(self.bondNameRule(at1, at2, "T")[0])
                if stick is not None:
                    vcolors = [self.retrieveAtColorFrom(at1, sel, colors, geom),
                               self.retrieveAtColorFrom(at2, sel, colors, geom)]
                    self._checkChangeMaterial(stick, fType, atom=at1, color=vcolors[0])
                stick = self.helper.getObject(self.bondNameRule(at2, at3, "T")[0])
                if stick is not None:
                    vcolors = [self.retrieveAtColorFrom(at2, sel, colors, geom),
                               self.retrieveAtColorFrom(at3, sel, colors, geom)]
                    self._checkChangeMaterial(stick, fType, atom=at3, color=vcolors[1])
            else:
                stick = self.helper.getObject(self.bondNameRule(at1, at3, "T")[0])
                if stick is not None:
                    vcolors = [self.retrieveAtColorFrom(at1, sel, colors, geom),
                               self.retrieveAtColorFrom(at3, sel, colors, geom)]
                    self._checkChangeMaterial(stick, fType, atom=at3, color=vcolors[1])

    def color(self, mol=None, mname=None, selection=None, lGeom=[], funcId=None):
        if mol is None:
            return
        if mname is None:
            mname = mol.name
        if funcId is None:
            funcId = self.mv.molDispl[mname]["col"]
        if selection == None:
            selection = mol
        #        print "colorF ", funcId,self.funcColor[funcId], lGeom
        if funcId == 7:
            # custom color
            color = self.mv.molDispl[mname]["col"]
            self.funcColor[7](selection, [color], lGeom, log=1)
        elif funcId == 8 or funcId == 9 or funcId == 10:
            # color by properties , ie NtoC, Bfactor, SAS
            self.mv.colorByProperty.level = 'Atom'
            if funcId == 8:
                # what about chain selection
                maxi = max(selection.number)  # selection[-1].number
                mini = min(selection.number)  # selection[0].number
                property = 'number'
            elif funcId == 9:
                maxi = max(selection.temperatureFactor)
                mini = min(selection.temperatureFactor)
                property = 'temperatureFactor'
            elif funcId == 10:
                if not hasattr(selection, "sas_area"):
                    try:
                        self.mv.computeSESAndSASArea(mol)
                    except:
                        self.drawError("Problem with mslib")
                maxi = max(selection.sas_area)
                mini = min(selection.sas_area)
                property = 'sas_area'
            #            print ("color",len(selection),property)
            self.funcColor[8](selection, lGeom, property, mini=float(mini),
                              maxi=float(maxi), propertyLevel='Atom',
                              colormap='rgb256')
            self.mv.molDispl[mname]["col"] = funcId
        else:
            self.funcColor[funcId](selection, lGeom)
            self.mv.molDispl[mname]["col"] = funcId

    def _color(self, mol, atms, options):
        """
        General Callback function reacting to any colorX commands. Call according
        function to change/update the object color.
        Note: should be optimized...

        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command
        """

        # color the list of geoms (options[0]) according the function (options[-1])
        lGeoms = options[0]
        fType = options[-1]
        command_colors = options[1]
        #        print ("color function",fType,lGeoms,command_colors)
        mol = mol[0]  # TO FIX
        sel = atms[0]
        #        print mol, sel, len(mol.allAtoms) != len(sel)
        selection = len(mol.allAtoms) != len(sel)
        chn = sel[0].getParentOfType(Chain)
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        #        print chn
        #        print test
        #        print lGeoms
        for geom in lGeoms:
            if geom == "secondarystructure":
                for ch in mol.chains:
                    if selection and ch is chn:
                        ch = chn
                    parent = self._getObject(chobj[ch.name + "_ss"])
                    if not hasattr(ch, "secondarystructureset"):
                        continue
                    for elem in ch.secondarystructureset:
                        # get the geom or the extruder ?
                        if hasattr(elem, "exElt"):
                            ex = elem.exElt
                        else:
                            continue
                        name = elem.name
                        colors = elem.exElt.colors
                        if colors is None:
                            # get the regular color for this SS if none is get
                            colors = [SecondaryStructureType[elem.structureType], ]
                        if hasattr(ex, "obj"):  # and self.host != "3dsmax":
                            g = mol.geomContainer.geoms[ex.ssElt.name + ch.name]
                            self._changeColor(g, colors, perVertex=False)  # perFaces color
                        if ch.ribbonType() == 'NA':
                            self._colorLadder(mol, ch, fType, None)
            elif geom == "SS":
                for ch in mol.chains:
                    if selection and ch is chn:
                        ch = chn
                    parent = self._getObject(chobj[ch.name + "_ss"])
                    name = "SS%s" % (ch.id)
                    g = mol.geomContainer.geoms[name]
                    colors = mol.geomContainer.getGeomColor(name)
                    flag = g.vertexArrayFlag
                    if hasattr(g, "obj"):
                        self._changeColor(g, colors, perVertex=flag,
                                          pb=self.use_progressBar)
            elif geom == "loft":
                for ch in mol.chains:
                    if selection and ch is chn:
                        ch = chn
                    parent = self._getObject("loft" + mol.name + "_" + ch.name)  # loft1crn_A
                    # should build a gradient material..lets just color the ladder if they exist
                    # and get first color for applying material on loft
                    # take the color from the selection color appyed
                    # print colors,len(command_colors),fType #selection colors
                    # tthis is per chains, so just take the id from the sel
                    for i in range(len(sel)):
                        if sel[i].getParentOfType(Chain) == ch:
                            colors = [command_colors[i]]
                            break
                    self._changeColor(parent, colors, perVertex=False)  # perFaces color
                    if ch.ribbonType() == 'NA':
                        self._colorLadder(mol, ch, fType, command_colors, bilader=True,
                                          name="loft", sel=sel)
            elif geom == "cpk" or geom == "balls":
                # have instance materials...so if colorbyResidue have to switch to residueMaterial
                parent = self.getSelectionCommand(sel, mol)
                g = mol.geomContainer.geoms[geom]
                colors = mol.geomContainer.getGeomColor(geom)
                # or do we use the options[1] which should be the colors ?
                prefix = "S"
                name = "cpk"
                if geom == "balls":
                    prefix = "B"
                    name = "bs"  # "balls&sticks"
                if len(sel) == len(mol.allAtoms):
                    p = mol.name + "_" + name
                else:
                    p = parent
                if hasattr(g, "obj"):
                    [self._colorSphere(x[1], x[0], sel,
                                       prefix, p, fType, geom) for x in enumerate(sel)]
            elif geom == "sticks":
                g = mol.geomContainer.geoms[geom]
                colors = mol.geomContainer.getGeomColor(geom)
                parent = self.getSelectionCommand(sel, mol)
                if hasattr(g, "obj"):
                    atoms = sel
                    set = mol.geomContainer.atoms["sticks"]
                    if len(set) == len(mol.allAtoms):
                        p = mol.name + "_cpk"
                    else:
                        p = parent
                    bonds, atnobnd = set.bonds
                    if len(set) != 0:
                        [self._colorStick(x[1], x[0], atoms, len(bonds), fType, p, mol) for x in enumerate(bonds)]
            else:
                # mostly these are polygon
                if geom in mol.geomContainer.geoms:
                    g = mol.geomContainer.geoms[geom]
                    colors = mol.geomContainer.getGeomColor(geom)
                    flag = g.vertexArrayFlag
                    if hasattr(g, "obj"):
                        self._changeColor(g, colors, perVertex=flag,
                                          pb=self.use_progressBar)
                    #                elif mol.geomContainer.geoms.has_key(geom):
                    #                    g = mol.geomContainer.geoms[geom[2:]]
                    #                    colors=mol.geomContainer.getGeomColor(geom)
                    #                    flag=g.vertexArrayFlag
                    #                    if hasattr(g,"obj"):
                    #                        self._changeColor(g,colors,perVertex=flag,
                    #                                              pb=self.use_progressBar)

    def _isoSurface(self, grid, options):
        """
        Callback for computing isosurface of grid volume data. will create and update
        the mesh showing the isosurface at a certain isovalue.

        @type  grid: Volume.Grid3D
        @param grid: the current grid volume data
        @type  options: list
        @param options: the list of option used for the command; ie isovalue, size...
        """
        if len(options) == 0:
            name = grid.name
            g = grid.srf
        else:
            name = options[0]
            g = grid.geomContainer['IsoSurf'][name]
        #            print name, g
        root = None
        if hasattr(self.mv, 'cmol') and self.mv.cmol != None:
            mol = self.mv.cmol
            root = mol.geomContainer.masterGeom.obj
        else:
            if hasattr(grid.master_geom, "obj"):
                root = grid.master_geom.obj
            else:
                root = self._newEmpty(grid.master_geom.name)
                self._addObjectToScene(self._getCurrentScene(), root)
                self._addObjToGeom(root, grid.master_geom)
        print ("isoC", name)
        if hasattr(g, "obj"):  # already computed so need update
            sys.stderr.write("UPDATE MESH")
            self._updateMesh(g)
        else:
            self.createMesh(name, g, proxyCol=True, parent=root)

    def piecewiseLinearInterpOnIsovalue(self, x):
        """Piecewise linear interpretation on isovalue that is a function
        blobbyness.
        """
        import sys
        X = [-3.0, -2.5, -2.0, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1]
        Y = [0.6565, 0.8000, 1.0018, 1.3345, 1.5703, 1.8554, 2.2705, 2.9382, 4.1485, 7.1852, 26.5335]
        if x < X[0] or x > X[-1]:
            print("WARNING: Fast approximation :blobbyness is out of range [-3.0, -0.1]")
            return None
        i = 0
        while x > X[i]:
            i += 1
        x1 = X[i - 1]
        x2 = X[i]
        dx = x2 - x1
        y1 = Y[i - 1]
        y2 = Y[i]
        dy = y2 - y1
        return y1 + ((x - x1) / dx) * dy

    def coarseMolSurface(self, molFrag, XYZd, isovalue=7.0, resolution=-0.3, padding=0.0,
                         name='CoarseMolSurface', geom=None):
        """
        Function adapted from the Vision network which compute a coarse molecular
        surface in PMV

        @type  molFrag: MolKit.AtomSet
        @param molFrag: the atoms selection
        @type  XYZd: array
        @param XYZd: shape of the volume
        @type  isovalue: float
        @param isovalue: isovalue for the isosurface computation
        @type  resolution: float
        @param resolution: resolution of the final mesh
        @type  padding: float
        @param padding: the padding
        @type  name: string
        @param name: the name of the resultante geometry
        @type  geom: DejaVu.Geom
        @param geom: update geom instead of creating a new one

        @rtype:   DejaVu.Geom
        @return:  the created or updated DejaVu.Geom
        """
        #        print molFrag
        #        print molFrag.top
        #        self.mv.assignAtomsRadii(molFrag.top, united=1, log=0, overwrite=0)
        from MolKit.molecule import Atom
        atoms = molFrag.findType(Atom)
        coords = atoms.coords
        radii = atoms.vdwRadius
        #        print len(radii),radii[0]
        #        print len(coords),coords[0]
        # self.assignAtomsRadii("1xi4g", united=1, log=0, overwrite=0)
        from UTpackages.UTblur import blur
        import numpy.oldnumeric as Numeric
        #        print "res",resolution
        volarr, origin, span = blur.generateBlurmap(coords, radii, XYZd, resolution, padding=0.0)
        volarr.shape = (XYZd[0], XYZd[1], XYZd[2])
        #        print volarr
        volarr = Numeric.ascontiguousarray(Numeric.transpose(volarr), 'f')
        #        print volarr

        weights = Numeric.ones(len(radii), typecode="f")
        h = {}
        from Volume.Grid3D import Grid3DF
        maskGrid = Grid3DF(volarr, origin, span, h)
        h['amin'], h['amax'], h['amean'], h['arms'] = maskGrid.stats()
        # (self, grid3D, isovalue=None, calculatesignatures=None, verbosity=None)
        from UTpackages.UTisocontour import isocontour
        isocontour.setVerboseLevel(0)

        data = maskGrid.data

        origin = Numeric.array(maskGrid.origin).astype('f')
        stepsize = Numeric.array(maskGrid.stepSize).astype('f')
        # add 1 dimension for time steps amd 1 for multiple variables
        if data.dtype.char != Numeric.Float32:
            #            print 'converting from ', data.dtype.char
            data = data.astype('f')  # Numeric.Float32)

        newgrid3D = Numeric.ascontiguousarray(Numeric.reshape(Numeric.transpose(data),
                                                              (1, 1) + tuple(data.shape)), data.dtype.char)
        #        print "ok"
        ndata = isocontour.newDatasetRegFloat3D(newgrid3D, origin, stepsize)

        #        print "pfff"
        isoc = isocontour.getContour3d(ndata, 0, 0, isovalue,
                                       isocontour.NO_COLOR_VARIABLE)
        vert = Numeric.zeros((isoc.nvert, 3)).astype('f')
        norm = Numeric.zeros((isoc.nvert, 3)).astype('f')
        col = Numeric.zeros((isoc.nvert)).astype('f')
        tri = Numeric.zeros((isoc.ntri, 3)).astype('i')
        isocontour.getContour3dData(isoc, vert, norm, col, tri, 0)
        # print vert

        if maskGrid.crystal:
            vert = maskGrid.crystal.toCartesian(vert)

        # from DejaVu.IndexedGeom import IndexedGeom
        from DejaVu.IndexedPolygons import IndexedPolygons
        if geom == None:
            g = IndexedPolygons(name=name)
        else:
            g = geom
        # print g
        inheritMaterial = None
        g.Set(vertices=vert, faces=tri, materials=None,
              tagModified=False,
              vnormals=norm, inheritMaterial=inheritMaterial)
        # shouldnt this only for the selection set ?
        g.mol = molFrag.top
        for a in atoms:  # g.mol.allAtoms:
            a.colors[g.name] = (1., 1., 1.)
            a.opacities[g.name] = 1.0
        self.mv.bindGeomToMolecularFragment(g, atoms)
        # print len(g.getVertices())
        return g

    def getCitations(self):
        citation = ""
        for module in self.mv.showCitation.citations:
            citation += self.mv.showCitation.citations[module]
        return citation

    def testNumberOfAtoms(self, mol):
        #        print "testNumberOfAtoms",mol
        nAtoms = len(mol.allAtoms)
        if nAtoms > self.max_atoms:
            mol.doCPK = False
        else:
            mol.doCPK = True

            # def piecewiseLinearInterpOnIsovalue(x):
        #            """Piecewise linear interpretation on isovalue that is a function
        #            blobbyness.
        #            """
        #            import sys
        #            X = [-3.0, -2.5, -2.0, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1]
        #            Y = [0.6565, 0.8000, 1.0018, 1.3345, 1.5703, 1.8554, 2.2705, 2.9382, 4.1485, 7.1852, 26.5335]
        #            if x<X[0] or x>X[-1]:
        #                print "WARNING: Fast approximation :blobbyness is out of range [-3.0, -0.1]"
        #                return None
        #            i = 0
        #            while x > X[i]:
        #                i +=1
        #            x1 = X[i-1]
        #            x2 = X[i]
        #            dx = x2-x1
        #            y1 = Y[i-1]
        #            y2 = Y[i]
        #            dy = y2-y1
        #            return y1 + ((x-x1)/dx)*dy

    #####EXTENSIONS FUNCTION
    def showMolPose(self, mol, pose, conf):
        """
        Show pyrosetta pose object which is a the result conformation of a
        simulation

        @type  mol: MolKit.Protein
        @param mol: the molecule node to apply the pose
        @type  pose: rosetta.Pose
        @param pose: the new pose from PyRosetta
        @type  conf: int
        @param conf: the indice for storing the pose in the molecule conformational stack
        """
        from Pmv.moleculeViewer import EditAtomsEvent
        pmv_state = conf
        import time
        if type(mol) is str:
            model = self.getMolFromName(mol.name)
        else:
            model = mol
        model.allAtoms.setConformation(conf)
        coord = {}
        #        print pose.n_residue(),len(model.chains.residues)
        for resi in range(1, pose.n_residue() + 1):
            res = pose.residue(resi)
            resn = pose.pdb_info().number(resi)
            # print resi,res.natoms(),len(model.chains.residues[resi-1].atoms)
            k = 0
            for atomi in range(1, res.natoms() + 1):
                name = res.atom_name(atomi).strip()
                if name != 'NV':
                    a = model.chains.residues[resi - 1].atoms[k]
                    pmv_name = a.name
                    k = k + 1
                    if name != pmv_name:
                        if name[1:] != pmv_name[:-1]:
                            print(name, pmv_name)
                        else:
                            coord[(resn, pmv_name)] = res.atom(atomi).xyz()
                            cood = res.atom(atomi).xyz()
                            a._coords[conf] = [cood.x, cood.y, cood.z]

                    else:
                        coord[(resn, name)] = res.atom(atomi).xyz()
                        cood = res.atom(atomi).xyz()
                        a._coords[conf] = [cood.x, cood.y, cood.z]  # return coord
        model.allAtoms.setConformation(conf)
        event = EditAtomsEvent('coords', model.allAtoms)
        self.dispatchEvent(event)
        # epmv.insertKeys(model.geomContainer.geoms['cpk'],1)

    #        self.helper.update()

    def updateDataGeom(self, mol):
        """
        Callback for updating special geometry that are not PMV generated and which
        do not react to editAtom event. e.g. pointCloud or Spline

        @type  mol: MolKit.Protein
        @param mol: the parent molecule
        """
        print ("updateDataGeom ", mol.name)
        # get the current selection if any
        allatoms = mol.allAtoms
        if self.current_selection is not None:
            print ("current selection have ", len(self.current_selection))
            allatoms = self.current_selection
        mname = mol.name
        disp = self.mv.molDispl[mname]
        print ("display dic ", disp)
        at = "CA"
        for i, c in enumerate(mol.chains):
            if c.ribbonType() == 'NA':
                at = "O5'"
            if "spline" in disp:
                if disp["spline"]:
                    self.helper.update_spline(mol.name + "_" + c.name + "spline", c.residues.atoms.get(at).coords)
            if "loft" in disp:
                if disp["loft"]:
                    if c.ribbonType() == 'NA':
                        # need to update the laders
                        self.updateNAlader("loft", mol, c)
                    # verify in c4d and blender
                    self.helper.update_spline("loft" + mol.name + "_" + c.name + "_spline", mol.allAtoms.get(at).coords)
            if "points" in disp:
                self.helper.updatePoly(mol.name + ":" + c.name + "_cloudds",
                                       vertices=c.residues.atoms.coords)
            if self.host == 'maya' and self.control_mmaya:
                # need to update visible object in mMaya
                ob = "chain_" + str(i) + "_particle"
                self.helper.updateParticle(ob, vertices=c.residues.atoms.coords,
                                           faces=None)
        if "lines" in disp:
            if disp["lines"]:
                self.mv.displayLines(mol.name)
        if "bead" in disp:
            if disp["bead"]:
                params = self.getStoreLastUsed(mol.name, "bead")
                if self.uniq_ss:
                    self.mv.beadedRibbonsUniq.redo = True
                    if type(params) is list or type(params) is tuple:
                        self.mv.beadedRibbonsUniq(mol, createEvents=False)
                    else:
                        self.mv.beadedRibbonsUniq(mol, createEvents=False, **params)
                else:
                    self.mv.beadedRibbons.redo = True
                    if type(params) is list or type(params) is tuple:
                        self.mv.beadedRibbons(mol, createEvents=False)
                    else:
                        self.mv.beadedRibbons(mol, createEvents=False, **params)
                self.mv.beadedRibbons.redo = False
        # what about selection? or per chain?
        if "surf" in disp:
            if disp["surf"]:
                self.updateMSMS(mol, allatoms)  # shoudl I redo the coloring?
        if "cms" in disp:
            if disp["cms"]:
                self.updateCMS(mol, allatoms)
        if "meta" in disp:
            if disp["meta"]:
                # check in other host
                self.helper.updateMetaball("metaballs" + mol.name, vertices=allatoms.coords)
        if "arm" in disp:
            if disp["arm"]:
                name = mol.name + "_Armature"
                # mol.geomContainer.geoms["armature"]=[object,bones,lsel]
                self._updateArmature(name, mol.geomContainer.geoms["armature"][2])
        if "cpk" in disp:
            if disp["cpk"]:
                # options = [False, False, 1, 0.0, 0, False, None, 'Molecule', False]
                g = mol.geomContainer.geoms['cpk']
                if hasattr(g, "obj"):
                    if len(g.obj) == len(mol.allAtoms):
                        # this will work if all atoms exist
                        for i, o in enumerate(g.obj):
                            if type(o) != str:
                                o = self.helper.getName(o)
                            self._updateSphereObj(o, mol.allAtoms[i].coords)
                    else:
                        for x in allatoms:  # or  selection
                            nameo = self.atomNameRule(x, "S")
                            self._updateSphereObj(nameo, x.coords)
        if "bs" in disp:
            if disp["bs"]:
                for x in allatoms:
                    fullname = self.atomNameRule(x, 'B')
                    self._updateSphereObj(fullname, x.coords)
                    bonds = x.bonds
                    for bond in bonds:
                        self._updateOneBond(bond)
                        # Particles?
        # look up for surface selection?
        if hasattr(mol, "has_particls") and mol.has_particls:
            # hostC = map(self.helper.FromVec,mol.allAtoms.coords)
            ids = range(len(mol.allAtoms))
        #            map(PS.SetPosition,ids,hostC)
        # self.helper.setProperty("position",ids,hostC)
        # Lines ?

        # look if there is a msms:
        #        #find a way to update MSMS and coarse
        #        if self.mv.molDispl[mname][3] : self.gui.updateMSMS()
        #        if self.mv.molDispl[mname][4] : self.gui.updateCMS()

    def updateData(self, traj, step):
        """
        Callback for updating molecule data following the data-player.
        DataType can be : MD trajectory, Model Data (NMR, DLG, ...)

        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        @type  step: int or float
        @param step: the new value to apply
        """
        print (traj, step)
        if traj[0] is not None:
            if traj[1] == 'traj':
                mol = traj[0].player.mol
                maxi = len(traj[0].coords)
                mname = mol.name
                if step < maxi:
                    traj[0].player.applyState(int(step))
                    self.updateDataGeom(mol)
            elif traj[1] == "model":
                mname = traj[0].split(".")[0]
                type = traj[0].split(".")[1]
                mol = self.mv.getMolFromName(mname)
                if type == 'model':
                    nmodels = len(mol.allAtoms[0]._coords)
                    if step < nmodels:
                        mol.allAtoms.setConformation(int(step))
                        # self.mv.computeSecondaryStructure(mol.name,molModes={mol.name:'From Pross'})
                        from Pmv.moleculeViewer import EditAtomsEvent
                        # event = EditAtomsEvent('coords', mol.allAtoms)
                        # self.mv.dispatchEvent(event)
                        self.updateDataGeom(mol)
                else:
                    nmodels = len(mol.docking.ch.conformations)
                    if step < nmodels:
                        mol.spw.applyState(step)
                        self.updateDataGeom(mol)

    def updateTraj(self, traj):
        """
        Callback for updating mini,maxi,default,step values needed by the data player
        DataType can be : MD trajectory, Model Data (NMR, DLG, ...)

        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        """

        if traj[1] == "model":
            mname = traj[0].split(".")[0]
            type = traj[0].split(".")[1]
            mol = self.mv.getMolFromName(mname)
            if type == 'model':
                nmodels = len(mol.allAtoms[0]._coords)
            else:
                nmodels = len(mol.docking.ch.conformations)
            mini = 0
            maxi = nmodels
            default = 0
            step = 1
        elif traj[1] == "traj":
            mini = 0
            maxi = len(traj[0].coords)
            default = 0
            step = 1
        elif traj[1] == "grid":
            mini = traj[0].mini
            maxi = traj[0].maxi
            default = traj[0].mean
            step = 0.01
        return mini, maxi, default, step

    def updateMSMS(self, mol, selection):
        # update color too ?
        if mol is None:
            return
        mname = mol.name
        name = 'MSMS-MOL' + mname
        pradius = self.gui.getReal(self.gui.SLIDERS["surf"])
        density = self.gui.getReal(self.gui.SLIDERS["surfdensity"])
        try:
            colorMod = self.mv.molDispl[mname]["col"]
        except:
            colorMod = None
        if pradius is None:
            pradius, density, colorMod = self.getStoreLastUsed(mname, "surf",
                                                               keys=["pradius", "density", "colorMod"])
        if pradius == 0.:
            return
        if density == 0.:
            return
        if name in mol.geomContainer.geoms:
            self.mv.computeMSMS(selection,  # hdensity=msmsopt['hdensity'].val,
                                hdset=None,
                                density=density,
                                pRadius=pradius,
                                perMol=0, display=True,
                                surfName=name)

            if colorMod is not None and self.updateColor:
                self.color(mol=mol, mname=mol.name, selection=selection,
                           lGeom=[name], funcId=colorMod)

    def updateCMS(self, mol, selection):
        # update color too ?
        if mol is None:
            return
        mname = mol.name
        name = 'CoarseMS_' + mname
        if name in list(mol.geomContainer.geoms.keys()):
            parent = mol.geomContainer.masterGeom.obj
            # this doesnt work with c4d rendering
            iso = self.gui.getReal(self.gui.SLIDERS["cmsI"])
            res = self.gui.getReal(self.gui.SLIDERS["cmsR"])
            gridsize = self.gui.getLong(self.gui.SLIDERS["cmsG"])
            try:
                colorMod = self.mv.molDispl[mname]["col"]
            except:
                colorMod = None
            if iso is None:
                iso, res, gridsize, colorMod = self.getStoreLastUsed(mname, "cms",
                                                                     keys=["iso", "res", "gridsize", "colorMod"])

            # isovalue=7.1#float(cmsopt['iso'].val),
            # resolution=-0.3#float(cmsopt['res'].val)
            if iso == 0.:
                return
            if res == 0.:
                return
            g = self.coarseMolSurface(selection, [gridsize, gridsize, gridsize],
                                      isovalue=iso,
                                      resolution=res,
                                      name=name,
                                      geom=mol.geomContainer.geoms[name])
            print ("updateMesh", g.mesh, g.obj, name)
            self.helper.updateMesh(g.mesh, vertices=g.getVertices(),
                                   faces=g.getFaces(), obj=name)
            if colorMod is not None and self.updateColor:
                self.color(mol=mol, mname=mol.name, selection=selection,
                           lGeom=[name], funcId=colorMod)

    def storeLastUsed(self, mname, key, vdic):
        if mname not in self.lastUsed:
            self.lastUsed[mname] = {}
        if key not in self.lastUsed[mname]:
            self.lastUsed[mname][key] = {}
        for k in vdic:
            self.lastUsed[mname][key][k] = vdic[k]

    def getStoreLastUsed(self, mname, key, keys=[]):
        if mname not in self.lastUsed:
            return [None, ] * len(keys)
        if key not in self.lastUsed[mname]:
            return [None, ] * len(keys)
        if not len(keys):
            return self.lastUsed[mname][key]
        res = []
        for k in keys:
            if k not in self.lastUsed[mname][key]:
                res.append(None)
            else:
                res.append(self.lastUsed[mname][key][k])
        return res

    def renderDynamic(self, traj, timeWidget=False, timeLapse=5):
        """
        Callback for render a full MD trajectory.

        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        @type  timeWidget: boolean
        @param timeWidget: use the timer Widget to cancel the rendering
        @type  timeLapse: int
        @param timeLapse: the timerWidget popup every timeLapse
        """
        if timeWidget:
            dial = self.helper.TimerDialog()
            dial.cutoff = 15.0
        if traj[0] is not None:
            if traj[1] == 'traj':
                mol = traj[0].player.mol
                maxi = len(traj[0].coords)
                mname = mol.name
                for i in range(maxi):
                    if timeWidget and (i % timeLapse) == 0:
                        dial.open()
                        if dial._cancel:
                            return False
                    traj[0].player.applyState(i)
                    self.updateDataGeom(mol)
                    if self.mv.molDispl[mname]["surf"]: self.gui.updateMSMS()
                    if self.mv.molDispl[mname]["cms"]: self.gui.updateCMS()
                    self.helper.update()
                    self._render("md%.4d" % i, 640, 480)
            elif traj[1] == 'model':
                mname = traj[0].split(".")[0]
                type = traj[0].split(".")[1]
                mol = self.mv.getMolFromName(mname)
                if type == 'model':
                    maxi = len(mol.allAtoms[0]._coords)
                    for i in range(maxi):
                        mol.allAtoms.setConformation(step)
                        # self.mv.computeSecondaryStructure(mol.name,molModes={mol.name:'From Pross'})
                        from Pmv.moleculeViewer import EditAtomsEvent
                        event = EditAtomsEvent('coords', mol.allAtoms)
                        self.mv.dispatchEvent(event)
                        self.updateDataGeom(mol)
                        if self.mv.molDispl[mname]["surf"]: self.gui.updateMSMS()
                        if self.mv.molDispl[mname]["cms"]: self.gui.updateCMS()
                        self.helper.update()
                        self._render("model%.4d" % i, 640, 480)

    def APBS(self):
        """ DEPRECATED AND NOT USE """
        # need the pqrfile
        # then can compute
        self.mv.APBSSetup.molecule1Select(molname)
        self.mv.APBSSetup({'solventRadius': 1.4, 'ions': [], 'surfaceCalculation':
            'Cubic B-spline',
                           'pdb2pqr_Path': '/Library/MGLTools/1.5.6.up/MGLToolsPckgs/MolKit/pdb2pqr/pdb2pqr.py',
                           'xShiftedDielectricFile': '',
                           'proteinDielectric': 2.0,
                           'projectFolder': 'apbs-project',
                           'zShiftedDielectricFile': '',
                           'complexPath': '', 'splineBasedAccessibilityFile': '',
                           'chargeDiscretization': 'Cubic B-spline',
                           'ionAccessibilityFile': '', 'gridPointsY': 65,
                           'chargeDistributionFile': '', 'ionChargeDensityFile': '',
                           'pdb2pqr_ForceField': 'amber', 'energyDensityFile': '',
                           'fineCenterZ': 22.6725, 'forceOutput': '', 'fineCenterX': 10.0905,
                           'fineCenterY': 52.523, 'potentialFile': 'OpenDX', 'splineWindow': 0.3,
                           'yShiftedDielectricFile': '', 'VDWAccessibilityFile': '',
                           'gridPointsX': 65, 'molecule1Path': '/Users/ludo/1M52mono.pqr',
                           'sdens': 10.0, 'coarseLengthY': 73.744,
                           'boundaryConditions': 'Single Debye-Huckel',
                           'calculationType': 'Electrostatic potential',
                           'fineLengthZ': 73.429, 'fineLengthY': 52.496,
                           'fineLengthX': 68.973, 'laplacianOfPotentialFile': '',
                           'saltConcentration': 0.01, 'pbeType': 'Linearized', 'coarseCenterX': 10.0905,
                           'coarseCenterZ': 22.6725, 'ionNumberFile': '', 'coarseCenterY': 52.523,
                           'name': 'Default', 'solventDielectric': 78.54, 'solventAccessibilityFile': '',
                           'APBS_Path': '/Library/MGLTools/1.5.6.up/MGLToolsPckgs/binaries/apbs',
                           'molecule2Path': '', 'coarseLengthX': 98.4595, 'kappaFunctionFile': '',
                           'coarseLengthZ': 105.1435, 'systemTemperature': 298.15, 'gridPointsZ': 65,
                           'energyOutput': 'Total'}, log=0)
        # then run
        self.mv.APBSRun('1M52mono', None, None, APBSParamName='Default',
                        blocking=False, log=0)
        # then read the dx grid
        self.Grid3DReadAny('/Library/MGLTools/1.5.6.up/bin/apbs-1M52mono/1M52mono.potential.dx',
                           normalize=False, log=0, show=False)

        # self.APBSMapPotential2MSMS(potential='/Library/MGLTools/1.5.6.up/bin/apbs-1M52mono/1M52mono.potential.dx', log=0, mol='1M52mono')

    def APBS2MSMS(self, grid, surf=None, offset=1.0, stddevM=5.0, rampcol=None):
        """
        Map a surface mesh using grid (APBS,AD,...) values projection.
        This code is based on the Pmv vision node network which color a
        MSMS using a APBS computation.

        @type  grid: grids3D
        @param grid: the grid to project
        @type  surf: DejaVu.Geom or hostApp mesh
        @param surf: the surface mesh to color
        @type  offset: float
        @param offset: the offset to apply to the vertex normal used for the projection
        @type  stddevM: float
        @param stddevM: scale factor for the standard deviation fo the grid data values
        """
        if rampcol is not None:
            col1, col2, col3 = rampcol
        else:
            col1 = blue
            col2 = white
            col3 = red
        v, f, vn, fn = self.getSurfaceVFN(surf)
        if v is None: return
        points = v + (vn * offset)
        data = self.TriInterp(grid, points)
        # need to apply some stddev on data
        datadev = util.stddev(data) * stddevM
        # need to make a colorMap from this data
        # colorMap should be the rgbColorMap
        # cmap = ePMV.__path__[0]+"/apbs_map.py"
        # lcol = self.colorMap(colormap='rgb256',mini=-datadev,
        #                     maxi=datadev,values=data,filename=cmap)
        from DejaVu.colorTool import Map
        from upy import colors
        ramp = colors.ThreeColorRamp(col1=col1, col2=col2, col3=col3)
        lcol = Map(data, ramp, mini=-datadev, maxi=datadev)
        #        if self.soft =="c4d":
        #            self._changeColor(surf,lcol,proxyObject=True)
        #        else :
        self._changeColor(surf, lcol)

    def getSurfaceVFN(self, geometry):
        """
        Extract vertices, faces and normals from either an DejaVu.Geom
        or a hostApp polygon mesh

        @type  geometry: DejaVu.Geom or hostApp polygon
        @param geometry: the mesh to decompose

        @rtype:   list
        @return:  faces,vertices,vnormals of the geometry
        """
        #        print "ok",geometry
        if geometry:
            if not hasattr(geometry, 'asIndexedPolygons'):
                f = None
                v = None
                vn = None
                f, v, vn = self.helper.DecomposeMesh(geometry, edit=False,
                                                     copy=False, tri=False,
                                                     transform=False)
                fn = None
            else:
                geom = geometry.asIndexedPolygons()
                v = geom.getVertices()
                vn = geom.getVNormals()
                fn = geom.getFNormals()
                f = geom.getFaces()
            return Numeric.array(v), f, Numeric.array(vn), fn

    def TriInterp(self, grid, points):
        """
        Trilinear interpolation of a list of point in the given grid.

        @type  grid: grid3D
        @param grid: the grid object
        @type  points: numpy.array
        @param points: list of point to interpolate in the grid

        @rtype:   list
        @return:  the interpolated value for the given list of point
        """

        values = []
        import numpy.oldnumeric as N
        from Volume.Operators.trilinterp import trilinterp

        origin = N.array(grid.origin, Numeric.Float32)
        stepSize = N.array(grid.stepSize, Numeric.Float32)

        invstep = (1. / stepSize[0], 1. / stepSize[1], 1. / stepSize[2])

        if grid.crystal:
            points = grid.crystal.toFractional(points)

        values = trilinterp(points, grid.data, invstep, origin)

        return values

    def colorMap(self, colormap='rgb256', values=None, mini=None, maxi=None, filename=None):
        """
        Prepare and setup a DejaVu.colorMap using the given options

        @type  colormap: str
        @param colormap: name of existing colormap
        @type  values: list
        @param values: list of color for the colormap
        @type  mini: float
        @param mini: minimum value for the ramp
        @type  maxi: float
        @param maxi: maximum value for the ramp
        @type  filename: str
        @param filename: colormap filename

        @rtype:   DejaVu.colorMap
        @return:  the prepared color map
        """
        from DejaVu.colorMap import ColorMap
        import types
        if colormap is None:
            pass  # colormap = RGBARamp
        elif type(colormap) is bytes \
                and colormap in self.mv.colorMaps:
            colormap = self.mv.colorMaps[colormap]
        if not isinstance(colormap, ColorMap):
            return 'ERROR'
        if values is not None and len(values) > 0:
            if mini is None:
                mini = min(values)
            if maxi is None:
                maxi = max(values)
            colormap.configure(mini=mini, maxi=maxi)
        if filename:
            colormap.read(filename)
            colormap.configure(mini=mini, maxi=maxi)
        if (values is not None) and (len(values) > 0):
            lCol = colormap.Map(values)
            if lCol is not None:
                return lCol.tolist()
        elif len(colormap.ramp) == 1:
            return colormap.ramp[0]
        else:
            return colormap.ramp

    def setEnvPyRosetta(self, extensionPath):
        # path = epmv.gui.inst.extdir[1]
        # epmv.setEnvPyRosetta(path)
        os.environ["PYROSETTA"] = extensionPath
        os.environ["PYROSETTA_DATABASE"] = extensionPath + os.sep + "minirosetta_database"
        if "DYLD_LIBRARY_PATH" not in os.environ:
            os.environ["DYLD_LIBRARY_PATH"] = ""
        os.environ["DYLD_LIBRARY_PATH"] = extensionPath + ":" + extensionPath + "/rosetta:" + os.environ[
            "DYLD_LIBRARY_PATH"]
        if "LD_LIBRARY_PATH" not in os.environ:
            os.environ["LD_LIBRARY_PATH"] = ""
        os.environ["LD_LIBRARY_PATH"] = extensionPath + "/rosetta:" + os.environ["LD_LIBRARY_PATH"]
        # this is not working! how can I do it

    def checkExtension(self):
        #        global _modeller,_useModeller,_AF,_AR,_inst
        listExtension = []
        if self.inst is None:
            self.setupInst()
        self.inst.getExtensionDirFromFile()
        for i, ext in enumerate(self.inst.extensions):
            if self.inst.extdir[i] not in sys.path:
                sys.path.append(self.inst.extdir[i])
                if ext.lower() == 'modeller':  # with 9.10
                    sys.path.insert(1, self.inst.extdir[i] + "/modlib")
                    sys.path.insert(1, self.inst.extdir[i] + "/lib")
                    if sys.platform == "darwin":  # if 11 there s 64bits support:
                        sys.path.insert(1, self.inst.extdir[i] + "/lib/mac10v4/python2.5")
                        # if arch=="64bit":
                        #    sys.path.insert(1,self.inst.extdir[i]+"/lib/mac10v4-intel64")
                        # else :
                        #    sys.path.insert(1,self.inst.extdir[i]+"/lib/mac10v4-intel")#this is for mac
                    elif sys.platform == "win32":
                        pass
                    elif sys.platform.find("linux") != -1:
                        if platform.architecture()[0] == "32bit":
                            sys.path.insert(1, self.inst.extdir[i] + "/lib/i386-intel8")  # which python ?
        if not self.useModeller:
            try:
                import modeller
                self._modeller = True
                listExtension.append('modeller')
            except:
                print("noModeller")
        if not self._AF:
            try:
                import AutoFill
                self._AF = True
                listExtension.append('AutoFill')
            except:
                print("noAutoFill")
        if not self._AR:
            try:
                import ARViewer
                self._AR = True
                listExtension.append('ARViewer')
            except:
                print("noARViewer")
        if not self._pymol:
            try:
                import chempy
                self._pymol = True
                listExtension.append('PyMol')
            except:
                print("no pymol")
        if not self._prody:
            try:
                import prody
                self._prody = True
                listExtension.append('Prody')
            except:
                print("no prody")
        return listExtension

    # from the helper, may change in c4d, maya to check

    def getGeomName(self, geom):
        g = geom
        name = "Pmv_"
        while g != geom.viewer.rootObject:
            # g.name can contain whitespaces which we have to get rid of
            gname = string.split(g.name)
            ggname = ""
            for i in gname:
                ggname = ggname + i
                name = name + string.strip(ggname) + "AT" + \
                       string.strip(str(g.instanceMatricesIndex)) + '_'
            g = g.parent
            name = string.replace(name, "-", "_")
        return name

    def findatmParentHierarchie(self, atm, indice, hiera):
        if indice == "S":
            n = 'cpk'
        else:
            n = 'balls'
        mol = atm.getParentOfType(Protein)
        hierarchy = self.parseObjectName(indice + "_" + atm.full_name())
        if hiera == 'perRes':
            parent = self.helper.getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
        elif hiera == 'perAtom':
            if atm1.name in backbone:
                parent = self.helper.getObject(atm.full_name() + "_bond")
            else:
                parent = self.helper.getObject(atm.full_name() + "_sbond")
        else:
            ch = atm.getParentOfType(Chain)
            parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[ch.name + "_" + n])
        return parent

    def parseObjectName(self, o, res=False):
        import re
        if type(o) == str or type(o) == str:
            name = o
        else:
            name = self.helper.getName(o)
        if name[0] in ["S", "B", "T"]:
            h = self.splitName(name)  # h isprefix,molname,chname,resname,rnum,atmnanme
            atn = h[-1]
            h[-1] = atn.replace('b', "'")
            # h[3] is one letter_code
            if res:
                rname = util.restoreR(h[3])
                return [h[1], h[2], rname + h[4], h[5]]
            else:
                return [h[1], h[2], int(h[4]), h[5]]
            #            if tmp[0] == "S" or tmp[0] == "B" : #balls or cpk
            #                if len(tmp) == 3 or len(tmp) > 5: #molname include '_'
            #                    hiearchy=name[2:].split(":")
            #                else :
            #                    hiearchy=tmp[1].split(":") #B.MOL.CHAIN.RESIDUE.ATOMS
            #                    if len(hiearchy) == 1 :
            #                        hiearchy=tmp[1:]
            #                atn = hiearchy[-1]
            ##                print "atn",atn
            #                hiearchy[-1] = atn.split("n")[0].replace('b',"'") #problem some atom have number.
            #            return hiearchy
        return ""

    def parseName(self, o):
        if type(o) == str:
            name = o
        else:
            name = self.helper.getName(o)
        tmp = name.split("_")
        if len(tmp) == 1:  # molname
            hiearchy = name.split(":")
            if len(hiearchy) == 1:
                return [name, ""]
            else:
                return hiearchy
        else:
            hiearchy = tmp[0].split(":")  # B_MOL:CHAIN:RESIDUE:ATOMS->i:j:
            return hiearchy

    def getIndiceMol(self, molname):
        for k in self.molDictionary:
            if molname == self.molDictionary[k][0]:
                return k, self.molDictionary[k][1]

    def bondNameRule(self, atom1, atom2, prefix):
        sep = "."
        if self.host == "maya":
            sep = "_"
        mindice, mvindice = self.getIndiceMol(
            atom1.top.name)  # self.mv.Mols.name.index(atom1.top.name) #self.molDictionary
        chindice = self.mv.Mols[mvindice].chains.name.index(atom1.parent.parent.name)
        mindice2, mvindice = self.getIndiceMol(atom2.top.name)  # self.mv.Mols.name.index(atom2.top.name)
        chindice2 = self.mv.Mols[mvindice].chains.name.index(atom2.parent.parent.name)
        if chindice != chindice2:
            print("different chain for the bonds atoms ?")
        mol = str(mindice)
        ch = str(chindice)
        if self.usefullname:
            mol = atom1.top.name
            ch = atom1.parent.parent.name
            # this is too long for blender2.49 and 2.6
        #        name1=prefix+sep+mol+sep+ch+sep+util.changeR(atom1.parent.name)+sep+atom1.name+sep+str(atom1.number)+sep+atom2.name+sep+str(atom2.number)
        #        name2=prefix+sep+mol+sep+ch+sep+util.changeR(atom1.parent.name)+sep+atom2.name+sep+str(atom2.number)+sep+atom1.name+sep+str(atom1.number)
        name1 = prefix + sep + mol + sep + ch + sep + atom1.name + sep + str(
            atom1.number) + sep + atom2.name + sep + str(atom2.number)
        name2 = prefix + sep + mol + sep + ch + sep + atom2.name + sep + str(
            atom2.number) + sep + atom1.name + sep + str(atom1.number)
        return name1.replace("'", "b"), name2.replace("'", "b")

    def atomNameRule(self, atom, prefix):
        # problem if I delete a molecule
        sep = "."
        if self.host == "maya":
            sep = "_"
        mindice, mvindice = self.getIndiceMol(atom.top.name)
        # mindice = self.mv.Mols.name.index(atom.top.name)
        chindice = self.mv.Mols[mvindice].chains.name.index(atom.parent.parent.name)
        mol = str(mindice)
        ch = str(chindice)
        if self.usefullname:
            mol = atom.top.name
            ch = atom.parent.parent.name
        #        print (mol,sep,ch,atom.parent.name,atom.name)
        #        print (util.changeR(atom.parent.name))
        fname = mol + sep + ch + sep + util.changeR(atom.parent.name) + sep + atom.name
        cleaned = fname.replace(":", sep).replace(" ", sep).replace("'", "b")
        name = prefix + sep + cleaned + sep + str(atom.number)
        return name

    def splitName(self, name):
        # general function-> in the adaptor ?
        # this function is overwrite in maya
        # depentd on atom name rules
        sep = "."
        if self.host == "maya":
            sep = "_"
        if name[0] == "T":
            tmp = name.split(sep)  # 'S.0.A.T1.N.0'
            indice = tmp[0]
            if not self.usefullname:
                # check indice in self.molDictionary,tmp1 is the molDictionary indice
                mindice = self.molDictionary[int(tmp[1])][1]
                molname = self.mv.Mols[mindice].name
                chainname = self.mv.Mols[int(tmp[1])].chains[int(tmp[2])].name
            else:
                molname = tmp[1]
                chainname = tmp[2]
            residuename = tmp[3][0:1]
            residuenumber = tmp[3][1:]
            atomname1 = tmp[4]
            return [indice, tmp[1], tmp[2], tmp[3][0:1], tmp[3][1:], tmp[4]]
        elif name[0] in ["S", "B", "L"]:
            tmp = name.split(sep)  # 'S.0.A.THR1.N.1'
            indice = tmp[0]
            if self.usefullname:
                molname = tmp[1]
                chainname = tmp[2]
            else:
                mindice = self.molDictionary[int(tmp[1])][1]
                molname = self.mv.Mols[mindice].name
                chainname = self.mv.Mols[int(tmp[1])].chains[int(tmp[2])].name
            residuename = tmp[3][0:1]
            residuenumber = tmp[3][1:]
            atomname = tmp[4]
            return [indice, molname, chainname, residuename, residuenumber, atomname]
        else:
            print("splitname", name)

    def _addObjToGeom(self, obj, geom):
        if type(obj) == list or type(obj) == tuple:
            if len(obj) > 2:
                geom.obj = obj
            elif len(obj) == 1:
                geom.obj = self.helper.getName(obj[0])
                geom.mesh = self.helper.getName(obj[0])
            elif len(obj) == 2:
                if type(obj[0]) == list or type(obj[0]) == tuple:
                    geom.obj = []
                    if type(obj[1]) == list or type(obj[1]) == tuple:
                        geom.mesh = obj[1][:]
                    elif type(obj[1]) == dict:
                        geom.mesh = {}
                        for me in list(obj[1].keys()):
                            geom.mesh[me] = self.helper.getName(obj[1][me])
                    else:
                        geom.mesh = self.helper.getName(obj[1])
                    geom.obj = obj[0][:]
                else:
                    geom.mesh = self.helper.getName(obj[1])
                    geom.obj = self.helper.getName(obj[0])
        else:
            geom.obj = self.helper.getName(obj)

    def setupMaterials(self):
        # Atoms Materials
        if self.helper is not None:
            self.helper.addMaterialFromDic(AtomElements)
            self.helper.addMaterialFromDic(DavidGoodsell)
            self.helper.addMaterial("A", (0.8, 1., 1.))
            self.helper.addMaterial("anyatom", (0.8, 1., 1.))
            self.helper.addMaterial("M", (0.8, 1., 1.))
            self.helper.addMaterial("Mg", (0.8, 1., 1.))
            self.helper.addMaterial("hetatm", (0., 1., 0.))
            self.helper.addMaterial("sticks", (0., 1., 0.))
        # Residues Materials
        self.RasmolAminocorrected = RasmolAmino.copy()
        for res in RasmolAminoSortedKeys:
            name = res.strip()
            if name in ['A', 'C', 'G', 'T', 'U']:
                name = 'D' + name
                self.RasmolAminocorrected[name] = RasmolAmino[res]
                del self.RasmolAminocorrected[res]
        if self.helper is not None:
            self.helper.addMaterialFromDic(self.RasmolAminocorrected)
        # SS Material
        SecondaryStructureType['Sheet'] = SecondaryStructureType['Strand']
        ssc = {}
        for ss in SecondaryStructureType:
            ssc[ss[:4]] = SecondaryStructureType[ss]
        if self.helper is not None:
            self.helper.addMaterialFromDic(ssc)

    def getAtomMaterial(self, atomname):
        mat = self.helper.getMaterial("anyatom")
        try:
            if atomname not in list(AtomElements.keys()) and \
                            atomname not in list(DavidGoodsell.keys()) and \
                            atomname != 'M':
                mat = self.helper.getMaterial('A')
            else:
                mat = self.helper.getMaterial("anyatom")
            return mat
        except:
            return None

    def _checkChangeMaterial(self, o, typeMat, atom=None, parent=None, color=None):
        # print typeMat
        # print "checkChangeMaterial"
        objmode = True
        matlist = self.helper.getAllMaterials()
        ss = "Helix"
        mol = None
        ch = None
        if atom is not None:
            res = atom.getParentOfType(Residue)
            ch = atom.getParentOfType(Chain)
            mol = atom.getParentOfType(Protein)
            if hasattr(res, 'secondarystructure'): ss = res.secondarystructure.name
        mats = self.helper.getMaterialObject(o)
        print ("object to color", o)
        print (mats)
        if mats is None or not mats:
            matname = ""
        else:
            matname = self.helper.getMaterialName(mats[0])
            # difficule to get the active one so just says ""
            if self.host == 'maya':
                matname = ""
        names = self.splitName(self.helper.getName(o))
        print ("current mat ", matname, names)
        newmat = None
        if typeMat == "":  # material by colorname-> function from rgb give color name...
            mat = self.helper.retrieveColorMat(color)
            # strange....why the "c" broke maya?
            e = "c"
            if self.host == "maya":
                e = ""
            if mat is None:
                mat = self.helper.getMaterial("rgb" + str(color[0])[0:3] + "_" + \
                                              str(color[1])[0:3] + "_" + str(color[2])[0:3] + e)
                if mat is None:
                    mat = self.helper.addMaterial("rgb" + str(color[0])[0:3] + \
                                                  "_" + str(color[1])[0:3] + "_" + str(color[2])[0:3] + e, color)
            self.helper.assignMaterial(o, [mat], objmode=objmode)
            newmat = mat
        else:
            self.changeMaterialSchemColor(typeMat)
            # print ("changeMaterialSchemColor",typeMat)
            if typeMat == "ByProp":  # color by color
                requiredMatname = self.helper.getName(o) + 'mat'
                #                print ("ByProp",requiredMatname,matname)
                rmat = self.helper.getMaterial(requiredMatname)
                cmat = self.helper.getMaterial(matname)
                print ("ByProp", rmat, cmat, cmat != rmat, requiredMatname not in matlist)
                if rmat is not None and cmat != rmat:
                    #                if matname != requiredMatname :
                    #                    print (requiredMatname)
                    if rmat not in matlist:
                        mat = self.helper.addMaterial(requiredMatname, color)
                        self.helper.assignMaterial(o, [mat], objmode=objmode)
                    else:
                        self.helper.colorMaterial(requiredMatname, color)
                        mat = self.helper.getMaterial(requiredMatname)
                        if mat is None:
                            mat = self.helper.addMaterial(requiredMatname, color)
                        self.helper.assignMaterial(o, [mat], objmode=objmode)  # should check if material are the same
                else:
                    if rmat not in matlist:
                        mat = self.helper.addMaterial(requiredMatname, color)
                        self.helper.assignMaterial(o, [mat], objmode=objmode)
                    else:
                        self.helper.colorMaterial(requiredMatname, color)
                        print ("colorMaterial(requiredMatname,color)")
                    newmat = requiredMatname
            elif typeMat == "ByAtom":
                #            print matname
                # if str(matname) not in list(self.AtmRadi.keys()) : #switch to atom materials
                #                    print (atom.name[0],names,names[5][0])
                #                    if names[5][0] not in list(AtomElements.keys()) :
                n = atom.name[0]  # names[5][0]
                if n not in list(AtomElements.keys()):
                    self.helper.assignMaterial(o, [self.helper.getMaterial('A')], objmode=objmode)
                else:
                    mat = self.helper.getMaterial(n)
                    self.helper.assignMaterial(o, [self.helper.getMaterial(n)], objmode=objmode)
                    #            else :
                    #                self.helper.colorMaterial(matname,AtomElements[names[5][0]])
                newmat = n
            elif typeMat == "AtomsU":
                name = self.lookupDGFunc(atom)
                if name not in list(DavidGoodsell.keys()):
                    self.helper.assignMaterial(o, [self.helper.getMaterial('A')], objmode=objmode)
                else:
                    self.helper.assignMaterial(o, [self.helper.getMaterial(name)], objmode=objmode)
            elif typeMat == "ByResi" or typeMat == "Residu":
                rname = res.type.replace(" ", "")
                if rname in ['A', 'C', 'G', 'T', 'U']:
                    rname = 'D' + rname
                    # if matname not in list(self.RasmolAminocorrected.keys()):
                if rname not in list(self.RasmolAminocorrected.keys()):
                    rname = 'hetatm'
                self.helper.assignMaterial(o, [self.helper.getMaterial(rname)], objmode=objmode)
                newmat = rname
            elif typeMat == "BySeco":
                # if matname not in self.ssk : #switch to ss materials
                self.helper.assignMaterial(o, [self.helper.getMaterial(ss[0:4])], objmode=objmode)
                newmat = ss[0:4]
            elif typeMat == "ByChai":
                # if matname is not ch.material : #switch to ch materials
                chmat = self.helper.getMaterial(ch.material)
                if chmat == None:
                    ch_colors = self.mv.colorByChains.palette.lookup(mol.chains)
                    chmat = self.helper.addMaterial(ch.material, ch_colors[ch.number])
                self.helper.assignMaterial(o, [chmat], objmode=objmode)
                newmat = chmat
            elif typeMat == "ByDoma":
                # if matname is not "domain"+str(atom.domainFragmentNumber) : #switch to ch materials
                chmat = self.helper.getMaterial("domain" + str(atom.domainFragmentNumber))
                if chmat == None:
                    ch_colors = self.mv.colorByChains.palette.lookup([atom])
                    chmat = self.helper.addMaterial("domain" + str(atom.domainFragmentNumber), ch_colors[0])
                self.helper.assignMaterial(o, [chmat], objmode=objmode)
                newmat = chmat

                # assign linking material for object
            #        if self.host == 'maya' :
            #            name = atom.name[0]
            #            if name not in AtomElements.keys() :
            #                    name = 'A'
            #            self.helper.connectAttr("crn_b_cpk_"+name+"Shape",material=mat)

    def changeMaterialSchemColor(self, typeMat):
        if typeMat == "ByAtom":
            [self.helper.colorMaterial(atms, AtomElements[atms]) for atms in list(AtomElements.keys())]
        elif typeMat == "AtomsU":
            [self.helper.colorMaterial(atms, DavidGoodsell[atms]) for atms in list(DavidGoodsell.keys())]
        elif typeMat == "ByResi":
            [self.helper.colorMaterial(res.strip(), self.RasmolAminocorrected[res]) \
             for res in list(self.RasmolAminocorrected.keys())]
        elif typeMat == "Residu":
            [self.helper.colorMaterial(res, Shapely[res]) for res in list(Shapely.keys())]
        elif typeMat == "BySeco":
            [self.helper.colorMaterial(ss[0:4], SecondaryStructureType[ss]) \
             for ss in list(SecondaryStructureType.keys())]
        else:
            pass

    def getSphereType(self, name):

        n = 'S'
        nn = 'cpk'
        if name.find('balls') != (-1):
            n = 'B'
            nn = 'balls'
        return n, nn

    def oneAtomSphere(self, at, n, iMe, parent=None):
        radius = at.radius
        atN = at.name
        if atN[0] not in list(AtomElements.keys()): atN = "A"
        fullname = self.atomNameRule(at, n)
        atC = at.coords  # at._coords[0]
        # create an instanceif sphere using the following mesh
        if atN[0] in iMe:
            # print (atN[0],iMe[atN[0]])
            sm = self.helper.getObject(iMe[atN[0]])  # or get mesh ?
        #            print (sm)
        else:
            #            print (iMe["A"])
            sm = self.helper.getObject(iMe["A"])
        #        print ("instance ",sm)
        #        print ("from ",iMe)
        mat = self.helper.getMaterial(atN[0])
        if mat is None:
            self.setupMaterials()
            mat = self.helper.getMaterial(atN[0])
        if self.use_instances:
            sp = self.helper.newInstance(fullname, sm, location=atC, parent=parent, material=mat)
        else:
            sp = self.helper.newClone(fullname, sm, location=atC, parent=parent, material=mat)
        #        sc = self.helper.getScale(sm)[0]
        # we can compare to at.vwdRadius
        #        if sc != radius :
        #            print(("rad",sc,radius,at.name))
        return sp

    def _instancesAtomsSphere(self, name, x, iMe, scn, mat=None, scale=1.0, Res=32,
                              R=None, join=0, geom=None, dialog=None, pb=False):
        # radius made via baseMesh...
        # except for balls, need to scale?#by default : 0.3?
        if scn == None:
            scn = self.helper.getCurrentScene()
        sphers = []
        if geom is not None and hasattr(geom, "obj"):
            sphers = geom.obj

        k = 0
        n, nn = self.getSphereType(name)  # S/B cpk/balls
        # get coordinate for the Sphere
        if geom is not None:
            coords = geom.getVertices()
        else:
            coords = x.coords
        hiera = self.useTree  # 'default' #None#'perRes' #or perAtom
        #        parent=self.findatmParentHierarchie(x[0],n,hiera)
        mol = x[0].getParentOfType(Protein)
        if pb:
            self.helper.resetProgressBar()
            self.helper.progressBar(progress=0, label="creating " + name)
        newSpheres = []
        for at in x:
            oneparent = True
            # atoms = c.residues.atoms
            c = at.parent.parent  # at.getParentOfType(Chain)#whih is at.parent.parent
            parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name + "_" + nn])
            fullname = self.atomNameRule(at, n)
            o = self.helper.getObject(fullname)
            if o is None:
                o = self.oneAtomSphere(at, n, iMe, parent=parent)
            else:
                self.helper.toggleDisplay(o, True)
            print ("one sphere")
            newSpheres.append(o)
            k = k + 1
            if pb:
                self.helper.progressBar(progress=k / len(coords))
                self.helper.update()
        if pb:
            self.helper.resetProgressBar(0)
        for s in sphers:
            if s not in newSpheres:
                o = self.helper.getObject(s)
                #                self.helper.deleteObject(o)
                self.helper.toggleDisplay(o, False)
        return newSpheres

    def oneStick(self, atm1, atm2, hiera, instance, parent, n=None):
        # mol=atm1.getParentOfType(Protein)
        c0 = numpy.array(atm1.coords)
        c1 = numpy.array(atm2.coords)
        # name1="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
        name = self.bondNameRule(atm1, atm2, "T")[0]
        # name="T_"+atm1.name.replace("'","b")+str(atm1.number)+"_"+atm2.name.replace("'","b")+str(atm2.number)
        #        if n is not None :
        #            name = n+name
        mat = self.helper.getMaterial('sticks')
        obj = self.helper.getObject(name)
        if obj is not None:
            self.helper.toggleDisplay(obj, True)
            return [obj]
        if self.use_instances:
            obj = self.helper.oneCylinder(name, c0, c1, instance=instance, material=mat, parent=parent)
        else:
            obj = self.helper.oneCylinder(name, c0, c1, material=mat, parent=parent)
            # if parent is not None : self.helper.reParent([obj,],parent)
        # self.helper.toggleDisplay(obj,display=False)
        return [obj]

    def biStick(self, atm1, atm2, hiera, instance, parent):
        mol = atm1.getParentOfType(Protein)
        c0 = numpy.array(atm1.coords)
        c1 = numpy.array(atm2.coords)
        vect = c1 - c0
        n1 = atm1.full_name().split(":")
        n2 = atm2.full_name().split(":")
        # should use the 1lettercode for residues to gain some space
        # ResidueSetSelector.r_keyD
        name1, name2 = self.bondNameRule(atm1, atm2, "T")
        if atm1.name[0] not in list(AtomElements.keys()):
            atN = "A"
        else:
            atN = atm1.name[0]
        mat = self.helper.getMaterial(atN)
        if type(mat) == type(None):
            mat = self.helper.addMaterial(atm1.name[0], [0., 0., 0.])
        obj1 = self.helper.getObject(name1)
        obj2 = self.helper.getObject(name2)
        if obj1 is not None and obj2 is not None:
            self.helper.toggleDisplay(obj1, True)
            self.helper.toggleDisplay(obj2, True)
            return obj1, obj2
        elif obj1 is not None:
            self.helper.toggleDisplay(obj1, True)
            return [obj1, None]
        elif obj2 is not None:
            self.helper.toggleDisplay(obj2, True)
            return [None, obj2]
        if self.use_instances:
            obj1 = self.helper.oneCylinder(name1, c0, (c0 + (vect / 2.)), instance=instance,
                                           material=mat, parent=parent)
        else:
            obj1 = self.helper.oneCylinder(name1, c0, (c0 + (vect / 2.)),
                                           material=mat, parent=parent)
        if atm2.name[0] not in list(AtomElements.keys()):
            atN = "A"
        else:
            atN = atm2.name[0]
        mat = self.helper.getMaterial(atN)
        if mat == None:
            mat = self.helper.addMaterial(atm2.name[0], [0., 0., 0.])
        # print c0
        if self.use_instances:
            obj2 = self.helper.oneCylinder(name2, (c0 + (vect / 2.)), c1, instance=instance,
                                           material=mat, parent=parent)
        else:
            obj2 = self.helper.oneCylinder(name2, (c0 + (vect / 2.)), c1,
                                           material=mat, parent=parent)
        return obj1, obj2

    #        self.helper.toggleDisplay(obj1,display=False)
    #        self.helper.toggleDisplay(obj2,display=False)
    #        print "."
    #        return obj1,obj2

    def createStickMaster(self, mol, res):
        sc = self.helper.getCurrentScene()
        # create mesh_baseBond
        parent = self.helper.newEmpty(mol.name + "_b_sticks")
        self.helper.addObjectToScene(sc, parent,
                                     parent=mol.geomContainer.masterGeom.obj)
        if self.host != "c4d":
            self.helper.toggleDisplay(parent, False)
        instance = self.helper.newEmpty(mol.name + "_b_sticks_shape")
        self.helper.addObjectToScene(sc, instance, parent=parent)
        cyl = self.helper.Cylinder(mol.name + "_b_sticks_o", res=res)[0]  # the objec
        self.helper.reParent(cyl, instance)
        #            self.helper.toggleDisplay(cyl,display=False)
        if self.host.find("blender") != -1:
            rad = 1.0
            if self.host == "blender24":
                rad = 0.5
            baseCyl, baseCylMesh = self.helper.Cylinder("baseCyl", radius=rad, length=1., res=res)
            self.helper.toggleDisplay(baseCyl, display=False)
            self.helper.toggleDisplay(cyl, display=False)
            instance = self.helper.getMesh("mesh_" + mol.name + "_b_sticks_o")
        elif self.host == "maya":
            #                self.helper.toggleDisplay(cyl,display=False)
            instance = cyl
        elif self.host == "c4d":
            instance = instance
            self.helper.toggleDisplay(parent, display=False)
        return instance

    def _doBS(self, sel, doSphere, doStick, name, gs=None, gb=None,
              # sticks options
              res=15, size=0.25, sc=2., bicyl=False,
              hiera='perRes',
              # balls options
              iMe=None, scale=1.0, Res=32, R=None,
              # options
              join=0, pb=False):
        sc = self.helper.getCurrentScene()
        sticks = []
        sphers = []
        newSpheres = []
        newSticks = []
        instance = None
        if doStick:
            if gs is not None and hasattr(gs, "obj"):
                sticks = gs.obj
            bonds, atnobnd = sel.bonds

            if gs is not None and hasattr(gs, "mesh"):
                instance = self.helper.getObject(gs.mesh)
            mol = bonds[0].atom1.top
            if instance == None:
                instance = self.createStickMaster(mol, res)

        if doSphere:
            if gb is not None and hasattr(gb, "obj"):
                sphers = gb.obj
            k = 0
            n, nn = self.getSphereType(name)  # S/B cpk/balls
            # get coordinate for the Sphere
            if gb is not None:
                coords = gb.getVertices()
            else:
                coords = sel.coords
        if not doSphere and not doStick:
            return sphers, [sticks, instance]

        hiera = self.useTree  # 'default'
        if pb:
            self.helper.resetProgressBar()
            self.helper.progressBar(progress=0, label="creating " + name)
        k = 0
        for at in sel:
            c = at.parent.parent
            oneparent = True
            bonds = at.bonds
            if hiera == 'default' or k == 0:
                parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name + "_balls"])
            elif hiera == 'perAtom':
                parent = self.helper.getObject(self.atomNameRule(sel[k - 1], 'B'))  # previous atom ?
            fullname = self.atomNameRule(at, 'B')
            if doSphere:
                o = self.helper.getObject(fullname)
                if o is None:
                    o = self.oneAtomSphere(at, 'B', iMe, parent=parent)
                else:
                    self.helper.toggleDisplay(o, True)
                # if o is not None :
                newSpheres.append(self.helper.getName(o))
            if doStick:
                #                print "ok len()", len(bonds)
                for bond in bonds:
                    if bicyl:
                        s = self.biStick(bond.atom1, bond.atom2,
                                         hiera, instance, parent=parent)
                        s = [self.helper.getName(s[0]), self.helper.getName(s[1])]
                    else:
                        s = self.oneStick(bond.atom1, bond.atom2,
                                          hiera, instance, parent=parent)
                        s = [self.helper.getName(s[0])]
                        # if s is not None :
                    #                    print s
                    newSticks.extend(s)
            k = k + 1
            if pb:
                self.helper.progressBar(progress=k / len(coords))
                self.helper.update()
        for s in sphers:
            if s not in newSpheres:
                o = self.helper.getObject(s)
                #                self.helper.deleteObject(o)
                self.helper.toggleDisplay(o, False)
        for x in sticks:
            if x not in newSticks:
                o = self.helper.getObject(x)
                #                print o
                #                self.helper.deleteObject(o)
                self.helper.toggleDisplay(o, False)

        if pb:
            self.helper.resetProgressBar(0)
        return newSpheres, [newSticks, instance]

    def _Tube(self, set, sel, points, faces, scn, armObj, res=32, size=0.25, sc=2., join=0,
              instance=None, hiera='perRes', bicyl=False, pb=False, g=None):
        sc = self.helper.getCurrentScene()
        sticks = []
        if g is not None and hasattr(g, "obj"):
            sticks = g.obj
        bonds, atnobnd = sel.bonds
        instance = None
        if g is not None and hasattr(g, "mesh"):
            instance = self.helper.getObject(g.mesh)
        #            print ("instane", instance)
        mol = bonds[0].atom1.top
        if instance == None:
            # create mesh_baseBond
            parent = self.helper.newEmpty(mol.name + "_b_sticks")
            self.helper.addObjectToScene(sc, parent,
                                         parent=mol.geomContainer.masterGeom.obj)
            if self.host != "c4d":
                self.helper.toggleDisplay(parent, False)
            instance = self.helper.newEmpty(mol.name + "_b_sticks_shape")
            self.helper.addObjectToScene(sc, instance, parent=parent)
            cyl = self.helper.Cylinder(mol.name + "_b_sticks_o", res=res)[0]  # the objec
            self.helper.reParent(cyl, instance)
            #            self.helper.toggleDisplay(cyl,display=False)
            if self.host.find("blender") != -1:
                rad = 1.0
                if self.host == "blender24":
                    rad = 0.5
                baseCyl, baseCylMesh = self.helper.Cylinder("baseCyl", radius=rad, length=1., res=res)
                self.helper.toggleDisplay(baseCyl, display=False)
                self.helper.toggleDisplay(cyl, display=False)
                instance = self.helper.getMesh("mesh_" + mol.name + "_b_sticks_o")
            elif self.host == "maya":
                #                self.helper.toggleDisplay(cyl,display=False)
                instance = cyl
            elif self.host == "c4d":
                instance = instance
                self.helper.toggleDisplay(parent, display=False)
        # use bonds from selection?
        # need bonds from selection
        for at in sel:
            c = at.getParentOfType(Chain)
            bonds = at.bonds
            parent = self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name + "_balls"])
            oneparent = True
            if pb:
                self._resetProgressBar()
                self._progressBar(0., 'creating bonds sticks')
            for bond in bonds:
                if bicyl:
                    s = self.biStick(bond.atom1, bond.atom2,
                                     hiera, instance, parent=parent)
                else:
                    s = self.oneStick(bond.atom1, bond.atom2,
                                      hiera, instance, parent=parent)
                if s is not None:
                    sticks.append(s)
                #        for c in mol.chains:
                #            stick=[]
                #            bonds, atnobnd = c.residues.atoms.bonds
                #            #parent = self.findatmParentHierarchie(bonds[0].atom1,'B',hiera)
                #            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name+"_balls"])
                ##            print c,parent
                #            oneparent=True
                #            if pb :
                #                self._resetProgressBar()
                #                self._progressBar(0., 'creating bonds sticks')
                #            stick = []
                #            if bicyl :
                #                stick = []
                #                stick = [self.biStick(bond.atom1,bond.atom2,
                #                                hiera,instance,parent=parent) for bond in bonds]
                #            else :
                #                stick = [self.oneStick(bond.atom1,bond.atom2,
                #                                hiera,instance,parent=parent) for bond in bonds]
                #            sticks.extend(stick)
        return [sticks, instance]

    def NAlader(self, name, mol, chain, res=32, size=0.25, sc=2., parent=None,
                join=0, instance=None, hiera='perRes', bicyl=False, pb=False,
                bilader=True):
        natype = {"A": "DA", "G": "DG", "C": "DC", "T": "DT", "U": "DU",
                  "DA": "DA", "DG": "DG", "DC": "DC", "DT": "DT", "DU": "DU",
                  "CBR": "DC"}
        residues = chain.residues
        total_res = len(residues)
        sc = self.helper.getCurrentScene()
        root = mol.geomContainer.masterGeom.obj
        if parent is not None:
            root = parent
        parent = self.helper.getObject(name + mol.name + chain.name + "_lader")
        if parent is None:
            parent = self.helper.newEmpty(name + mol.name + chain.name + "_lader")
            self.helper.addObjectToScene(sc, parent, parent=root)
        if instance == None:
            instance = self.helper.getObject(mol.name + "_b_lader_cyl")
            if instance is None:
                pinstance = self.helper.newEmpty(mol.name + "_b_lader_shape")
                self.helper.addObjectToScene(sc, pinstance,
                                             parent=mol.geomContainer.masterGeom.obj)
                instance = self.helper.newEmpty(mol.name + "_b_lader_cyl")
                self.helper.addObjectToScene(sc, instance,
                                             parent=pinstance)
                cyl = self.helper.Cylinder(mol.name + "_b_lader_o", res=res, radius=0.5)  # str,mes
                self.helper.reParent(cyl[0], instance)
            #            self.helper.toggleDisplay(cyl,display=False)
            if self.host == "blender25":
                instance = self.helper.getMesh("mesh_" + mol.name + "_b_lader_o")
            #            elif self.host == "maya":
            ##                self.helper.toggleDisplay(cyl,display=False)
            #                instance = cyl
            #            elif self.host == "c4d":
            #                instance = instance
        if pb:
            self._resetProgressBar()
            self._progressBar(0., 'creating dna/rna laders')
        # try P
        pinstance = self.helper.getObject(mol.name + "_b_lader_shape")
        basesphere = self.helper.getObject(mol.name + "_lader_sp")
        if basesphere is None:
            basesphere = self.helper.newEmpty(mol.name + "_lader_sp")
            self.helper.addObjectToScene(sc, basesphere, parent=pinstance)
            meshsphere, basesm = self.helper.Sphere(mol.name + "_lader_bsp",
                                                    parent=basesphere, radius=0.5)
        if self.host == "blender25":
            basesphere = self.helper.getMesh(mol.name + "_lader_bsp")
        # if self.host != "c4d":
        #    basesphere = self.helper.getMesh(mol.name+"_lader_bsp")
        sticks = []
        # parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name+"_balls"])
        for i in range(total_res):
            stick = []
            # need two point per residues P->C6 / C6->N3 C T
            # need two point per residues P->C8 / C8->N1 ['A', 'G', 'DA', 'DG']
            NA_type = residues[i].type.strip()
            try:
                # at1 = residues[i].atoms.objectsFromString('P')[0]
                at1 = residues[i].atoms.objectsFromString("O5'")[0]
            except:
                continue
                # at1 = residues[i].atoms[0]#take first atoms # or last ?
            if NA_type in ['A', 'G', 'DA', 'DG']:
                at2 = residues[i].atoms.objectsFromString('C8')[0]
                at3 = residues[i].atoms.objectsFromString('N1')[0]
            else:
                at2 = residues[i].atoms.objectsFromString('C6')[0]
                at3 = residues[i].atoms.objectsFromString('N3')[0]
            #            print "natype",NA_type,natype[NA_type],residues[i].name #CBR 21 ?? is a CYTIDINE
            mat = self.helper.getMaterial(natype[NA_type])  # of the resdiues
            if mat is None:
                mat = self.helper.getMaterial("A")
            #            print mat
            n = self.atomNameRule(at1, "L")
            sph = self.helper.newInstance(n, basesphere,
                                          location=at1.coords, parent=parent)
            #            self.helper.addObjectToScene(sc,sph,parent=parent)
            self.helper.assignMaterial(sph, mat)
            if bilader:
                n = self.atomNameRule(at2, "L")
                sph = self.helper.newInstance(n, basesphere,
                                              location=at2.coords, parent=parent)
                #                self.helper.addObjectToScene(sc,sph,parent=parent)
                self.helper.assignMaterial(sph, mat)
            n = self.atomNameRule(at3, "L")
            sph = self.helper.newInstance(n, basesphere,
                                          location=at3.coords, parent=parent)
            #            self.helper.addObjectToScene(sc,sph,parent=parent)
            self.helper.assignMaterial(sph, mat)

            if bilader:
                stick.extend(self.oneStick(at1, at2,
                                           hiera, instance, parent=parent, n=name))
                self.helper.assignMaterial(stick[-1], mat)
                stick.extend(self.oneStick(at2, at3,
                                           hiera, instance, parent=parent, n=name))
                self.helper.assignMaterial(stick[-1], mat)
            else:
                stick.extend(self.oneStick(at1, at3,
                                           hiera, instance, parent=parent, n=name))
                self.helper.assignMaterial(stick[-1], mat)
            sticks.extend(stick)
            if pb and (i % 10) == 0:
                progress = float(i) / len(total_res)
                self._progressBar(progress=progress)
        if pb:
            self._resetProgressBar()
            self._progressBar(0., 'creating dna/rna laders')
        return [parent, sticks, instance]

    def updateNAlader(self, name, mol, chain, pb=False, bilader=True):
        natype = {"A": "DA", "G": "DG", "C": "DC", "T": "DT", "U": "DU",
                  "DA": "DA", "DG": "DG", "DC": "DC", "DT": "DT", "DU": "DU"}
        residues = chain.residues
        total_res = len(residues)
        sc = self.helper.getCurrentScene()
        if pb:
            self._resetProgressBar()
            self._progressBar(0., 'update dna/rna laders')
        for i in range(total_res):
            stick = []
            # need two point per residues P->C6 / C6->N3 C T
            # need two point per residues P->C8 / C8->N1 ['A', 'G', 'DA', 'DG']
            NA_type = residues[i].type.strip()
            try:
                # at1 = residues[i].atoms.objectsFromString('P')[0]
                at1 = residues[i].atoms.objectsFromString("O5'")[0]
            except:
                continue
                # at1 = residues[i].atoms[0]#take first atoms # or last ?
            if NA_type in ['A', 'G', 'DA', 'DG']:
                at2 = residues[i].atoms.objectsFromString('C8')[0]
                at3 = residues[i].atoms.objectsFromString('N1')[0]
            else:
                at2 = residues[i].atoms.objectsFromString('C6')[0]
                at3 = residues[i].atoms.objectsFromString('N3')[0]
            # print "natype",NA_type,natype[NA_type],residues[i].name #CBR 21 ?? is a CYTIDINE
            c0 = numpy.array(at1.coords)
            c1 = numpy.array(at2.coords)
            c2 = numpy.array(at3.coords)
            self.setTranslation(name + at1.full_name(), pos=c0)
            self.setTranslation(name + at3.full_name(), pos=c2)
            if bilader:
                self.setTranslation(at2.full_name(), pos=c1)
                name = name + "T_" + at1.name.replace("'", "b") + str(at1.number) + "_" + at2.name.replace("'",
                                                                                                           "b") + str(
                    at2.number)
                o = self.helper.getObject(name)
                self._updateTubeObj(o, c0, c1)
                name = name + "T_" + at2.name.replace("'", "b") + str(at2.number) + "_" + at3.name.replace("'",
                                                                                                           "b") + str(
                    at3.number)
                o = self.helper.getObject(name)
                self._updateTubeObj(o, c1, c2)
            else:
                name = name + "T_" + at1.name.replace("'", "b") + str(at1.number) + "_" + at3.name.replace("'",
                                                                                                           "b") + str(
                    at3.number)
                o = self.helper.getObject(name)
                self._updateTubeObj(o, c0, c2)
            if pb and (i % 10) == 0:
                progress = float(i) / len(total_res)
                self._progressBar(progress=progress)
        if pb:
            self._resetProgressBar()
            # self._progressBar(0., 'creating dna/rna laders')
        return True

    def _editLines(self, molecules, atomSets):
        pass

    def _updateLines(self, lines, chains=None):
        # lines = getObject(name)
        # if lines == None or chains == None:
        # print lines,chains
        parent = self.helper.getObject(chains.full_name())
        # print parent
        bonds, atnobnd = chains.residues.atoms.bonds
        indices = [(x.atom1._bndIndex_,
                    x.atom2._bndIndex_) for x in bonds]
        self.helper.updatePoly(lines, vertices=chains.residues.atoms.coords, faces=indices)

    def _updateMesh(self, geom):
        print ("_updateMesh from", geom, geom.mesh)
        print ("name of the mesh ", self.helper.getName(geom.mesh))
        if self.host == '3dsmax':
            mesh = self.helper.getMesh(geom.mesh)
        else:
            mesh = self.helper.getMesh(self.helper.getName(geom.mesh))
        print ("update ", geom, mesh, geom.mesh, geom.obj)
        if not hasattr(geom, "getVertices"):
            # this os probably a extEl then just get vertices and faces
            vertices = geom.vertices
            faces = geom.faces
        else:
            vertices = geom.getVertices()
            faces = geom.getFaces()
        #        print ("updateMesh",geom.mesh,geom.obj,geom.name)
        # shouldnt use updatePoly ?
        self.helper.updateMesh(mesh, vertices=vertices,
                               faces=faces, obj=geom.name)

    def _updateTubeMesh(self, geom, quality=0.0, cradius=1.0):
        if self.use_instances:
            self.helper.updateTubeMesh(geom.mesh, basemesh="mesh_baseCyl",
                                       cradius=cradius, quality=quality)

    def _updateSphereMesh(self, geom, quality=0.0, cpkRad=0.0, scale=1.0, radius=None, prefix="B"):
        # compute the scale transformation matrix
        if not hasattr(geom, 'mesh'): return
        """segments=quality*5
        rings=quality*5
        if quality == 0 :
            segments = 25
            rings = 25"""
        # names=NMesh.GetNames()
        if self.use_instances:
            for name in list(geom.mesh.values()):
                #            print name
                #            basemesh =  self.helper.getMesh("mesh_basesphere")
                if name[-1] not in self.AtmRadi:
                    name = name[:-1] + "A"
                factor = float(cpkRad) + float(self.AtmRadi[name[-1]]) * float(scale)
                print ("sphere ", name)
                if hasattr(self, 'spherestype'):
                    self.helper.updateSphereMesh(name, basemesh="mesh_basesphere",
                                                 scale=factor, typ=self.spherestype, instance_master=False)
                else:
                    self.helper.updateSphereMesh(name, basemesh="mesh_basesphere",
                                                 scale=factor, instance_master=False)

    def updateMolAtomCoord(self, mol, index=-1, types='cpk'):
        # just need that cpk or the balls have been computed once..
        # balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        if index == -1: index = 0
        if types == 'cpk':
            vt = self.updateMolAtomCoordCPK(mol)
            mol.allAtoms.updateCoords(vt, ind=index)
        elif types == 'lines':
            vt = self.updateMolAtomCoordLines(mol)
            #            print vt[0]
            mol.allAtoms.updateCoords(vt, ind=index)
        elif types == 'bones':
            vt = self.updateMolAtomCoordBones(mol)
            # update lsel
            lsel = mol.geomContainer.geoms["armature"][2]
            if isinstance(lsel, AtomSet):
                #                print len(lsel),len(vt)
                #                print lsel
                lsel.updateCoords(vt, ind=index)
            else:
                pass
        elif types == 'spline':
            vt = self.updateMolAtomCoordSpline(mol)
            for i, c in enumerate(mol.chains):
                if c.ribbonType() == 'NA':
                    lsel = c.residues.atoms.get("O5'")
                else:
                    lsel = c.residues.atoms.get("CA")
                #                print len(lsel),len(vt),len(vt[i])
                lsel.updateCoords(vt[i], ind=index)

    def updateMolAtomCoordCPK(self, mol):
        """
        Return each CPK spheres absolute position for the specified mol.

        @type  mol: Molkit protein
        @param mol: the molecule from which the cpk sphere position will be get.
        @rtype:   array
        @return:  the xyz positions coordinates  of the CPK spheres
        """
        sph = mol.geomContainer.geoms['cpk'].obj
        vt = [self.helper.ToVec(self.helper.getTranslation(x)) for x in sph]
        #        print vt[0]
        return vt

    def updateCoordFromObj(self, sel, debug=True):
        mv = self.mv
        s = None
        if len(sel):
            # take first object selected?
            s = sel[0]
        #            print "in epmv ",s
        #            print "of type ", self.helper.getType(s)
        if s is not None:
            # print s.GetName()
            if self.helper.getType(s) == self.helper.SPLINE:
                print("ok Spline")
                # select = s.GetSelectedPoints()#mode=P_BASESELECT)#GetPointAllAllelection();
                # print nb_points
                # selected = select.get_all(s.GetPointCount()) # 0 uns | 1 selected
                # print selected
                # assume one point selected ?
                # selectedPoint = selected.index(1)
                # updateRTSpline(s,selectedPoint)
            if self.helper.getType(s) == self.helper.EMPTY or \
                            self.helper.getType(s) == self.helper.INSTANCE or \
                            self.helper.getType(s) == self.helper.SPLINE or \
                            self.helper.getType(s) == self.helper.BONES or \
                            self.helper.getType(s) == self.helper.POLYGON or \
                            self.helper.getType(s) == self.helper.IK:
                #                print "ok null"
                # molname or molname:chainname or molname:chain_ss ...
                hi = self.parseName(self.helper.getName(s))
                #                print "parsed ",hi
                if len(hi) == 1:
                    hi = [hi[0], ""]
                molname = hi[0]
                chname = hi[1]
                # mg = s.GetMg()
                # should work with chain level and local matrix
                # mg = ml = s.get_ml()
                # print molname
                # print mg
                # print ml
                if hasattr(mv, 'energy'):  # ok need to compute energy
                    # first update obj position: need mat_transfo_inv attributes at the mollevel
                    # compute matrix inverse of actual position (should be the receptor...)
                    if hasattr(mv.energy, 'amber'):
                        # first update obj position: need mat_transfo_inv attributes at the mollevel
                        mol = mv.energy.mol
                        if mol.name == molname:
                            if mv.minimize == True:
                                amb = mv.Amber94Config[mv.energy.name][0]
                                self.updateMolAtomCoord(mol, index=mol.cconformationIndex)
                                # mol.allAtoms.setConformation(mol.cconformationIndex)
                                # from Pmv import amberCommands
                                # amberCommands.Amber94Config = {}
                                # amberCommands.CurrentAmber94 = {}
                                # amb_ins = Amber94(atoms, prmfile=filename)
                                mv.setup_Amber94(mol.name + ":", mv.energy.name, mol.prname,
                                                 indice=mol.cconformationIndex)
                                mv.minimize_Amber94(mv.energy.name, dfpred=10.0, callback_freq='10', callback=1,
                                                    drms=1e-06, maxIter=100., log=0)
                                # mv.md_Amber94(mv.energy.name, 349, callback=1, filename='0', log=0, callback_freq=10)
                                # print "time"
                                # import time
                                # time.sleep(1.)
                                # mol.allAtoms.setConformation(0)
                                # mv.minimize = False
                    else:
                        rec = mv.energy.current_scorer.mol1
                        lig = mv.energy.current_scorer.mol2
                        if rec.name == molname or lig.name == molname:
                            use = "cpk"
                            if self.host != "maya":
                                use = "lines"
                            self.updateMolAtomCoord(rec, rec.cconformationIndex, types=use)
                            # mv.displayCPK(rec,redo=1)
                            self.updateMolAtomCoord(lig, lig.cconformationIndex, types='cpk')
                        if mv.energy.realTime:
                            if hasattr(mv, 'art'):
                                if not mv.art.frame_counter % mv.art.nrg_calcul_rate:
                                    self.get_nrg_score(mv.energy)
                            else:
                                self.get_nrg_score(mv.energy)
                        # should we try to optimize here, lets try the rec
                        if hasattr(rec, 'pmvaction'):
                            if rec.pmvaction.realtime:
                                rec.pmvaction.redraw = False
                                # synchronize current structure with modeller
                                # updateMolAtomCoord(mol,mol.pmvaction.idConf,types=mol.pmvaction.sObject)
                                rec.pmvaction.updateModellerCoord(rec.pmvaction.idConf, rec.mdl)
                                # conjugate_gradients
                                rec.pmvaction.modellerOptimize(rec.pmvaction.mdstep,
                                                               rec.pmvaction.temp)
                else:
                    for mol in mv.Mols:
                        #                        print "ok ",mol
                        if hasattr(mol, 'pmvaction'):
                            #                            print "pmvaction"
                            if mol.pmvaction.realtime:
                                #                                print "lets modeller"
                                mol.pmvaction.redraw = False
                                # synchronize current structure with modeller
                                self.updateMolAtomCoord(mol, mol.pmvaction.idConf,
                                                        types=mol.pmvaction.sObject)
                                mol.pmvaction.updateModellerCoord(mol.pmvaction.idConf, mol.mdl)
                                # conjugate_gradients
                                mol.pmvaction.modellerOptimize(mol.pmvaction.mdstep,
                                                               mol.pmvaction.temp)  # optimize and update coords
                            #                        else :
                            #                            self.updateMolAtomCoord(mol,1,types="")

    def colorByEnergy(self, atomSet, scorer, property):
        mini = min(getattr(atomSet, scorer.prop))
        # geomsToColor = vf.getAvailableGeoms(scorer.mol2)
        self.mv.colorByProperty(atomSet, ['cpk'], property,
                                mini=-1.0, maxi=1.0,
                                colormap='rgb256', log=1)  # ,

    def get_nrg_score(self, energy, display=True):
        # print "get_nrg_score"
        status = energy.compute_energies()
        #        print status
        if status is None: return
        #        print energy.current_scorer.score
        if hasattr(energy, 'labels') and energy.label:
            self.helper.updateText(energy.labels[0],
                                   string="score :" + str(energy.current_scorer.score)[0:5])
            for i, term in enumerate(['el', 'hb', 'vw', 'so']):
                labelT = energy.labels[i + 1]
                self.helper.updateText(labelT,
                                       string=term + " : " + str(energy.current_scorer.scores[i])[0:5])
        # change color of ligand with using scorer energy
        if energy.color[0] or energy.color[1]:
            # change selection level to Atom
            prev_select_level = self.mv.getSelLev()
            self.mv.setSelectionLevel(Atom, log=0)
            scorer = energy.current_scorer
            property = scorer.prop
            if energy.color[0]:
                atomSet1 = self.mv.expandNodes(scorer.mol1.name).findType(Atom)  # we pick the rec
                if hasattr(atomSet1, scorer.prop):
                    self.colorByEnergy(atomSet1, scorer, property)
            if energy.color[1]:
                atomSet2 = self.mv.expandNodes(scorer.mol2.name).findType(Atom)  # we pick the ligand
                if hasattr(atomSet2, scorer.prop):
                    self.colorByEnergy(atomSet2, scorer, property)

    def parse_symop_axis(self, op):
        rt = [0, 0, 0, 0]
        axis_names = ('X', 'Y', 'Z')
        for axis in range(3):
            axis_name = axis_names[axis]
            for (sym, sign) in (('+', 1), ('-', -1), ('', 1)):
                signed_name = sym + axis_name
                if op.find(signed_name) >= 0:
                    op = op.replace(signed_name, '')
                    rt[axis] = sign
        if op:
            fields = op.split('/')
            if len(fields) == 1:
                rt[3] = float(fields[0])
            elif len(fields) != 2:
                print('Bad symmetry operator component: ' + op)
            else:
                rt[3] = float(fields[0]) / float(fields[1])
        return rt

    def instanceMatricesFromGroup(self, molecule):
        from symserv.spaceGroups import spaceGroups
        from mglutil.math.crystal import Crystal
        returnMatrices = [numpy.eye(4, 4)]
        crystal = Crystal(molecule.cellLength, molecule.cellAngles)
        spgroup = molecule.spaceGroup.upper()
        if spgroup[-1] == " ":
            spgroup = spgroup[:-1]
        matrices = []
        if hasattr(molecule.parser, "mmCIF_dict"):
            if "_symmetry_equiv_pos_as_xyz" in molecule.parser.mmCIF_dict:
                # string representation of all symmetry.
                # transform to rot + trans
                for symop in molecule.parser.mmCIF_dict["_symmetry_equiv_pos_as_xyz"]:
                    symop = symop.replace("'", "")
                    tf = numpy.zeros((3, 4), float)
                    fields = symop.split(",")
                    for k in range(3):
                        tf[k, :] = self.parse_symop_axis(fields[k].upper())
                    matrices.append([tf[:3, :3], [tf[0][3], tf[1][3], tf[2][3]]])
        else:
            matrices = spaceGroups[spgroup]
        for matrix in matrices:
            tmpMatix = numpy.eye(4, 4)
            tmpMatix[:3, :3] = matrix[0]  # R
            tmpMatix[:3, 3] = crystal.toCartesian(matrix[1])  # T
            returnMatrices.append(tmpMatix)
        molecule.crystal = crystal
        return returnMatrices

    def buildCrystal(self, molecule, obj_to_instance=None):
        print ("buildCrystal ", molecule, obj_to_instance)
        if molecule is None:
            return
        if not hasattr(molecule, 'cellLength'):
            return
        if not hasattr(molecule, 'spaceGroup'):
            return
        name = molecule.name + "Crystals"
        parent = self.helper.getObject(name)
        if parent is None:
            parent = self.helper.newEmpty(name)
        matrices = self.instanceMatricesFromGroup(molecule)
        if obj_to_instance is None:
            obj_to_instance = molecule.geomContainer.geoms['master'].obj
        if type(obj_to_instance) == list or type(obj_to_instance) == tuple:
            obj_to_instance = obj_to_instance[0]
        molecule.crystal_pack = self.helper.instancePolygon(molecule.name + "_crystal_pack",
                                                            matrices=matrices,
                                                            mesh=obj_to_instance, parent=parent,
                                                            transpose=True, )
        if not molecule.geomContainer.geoms.has_key('Unit Cell'):
            fractCoords = ((1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 1),
                           (0, 0, 1), (1, 0, 1))
            coords = []
            # v,f,n = self.helper.hexahedron(1.0)
            coords = molecule.crystal.toCartesian(fractCoords)
            ob, obme = self.helper.createsNmesh(molecule.name + 'unitcell', coords, [], [])
            self.helper.reParent(ob, obj_to_instance)
            #            box=self.helper.Box('Unit Cell', vertices=coords)
            #            self.vf.GUI.VIEWER.AddObject(box, parent=geom)
            molecule.geomContainer.geoms['Unit Cell'] = ob

    def parse_PDB_BIOMT(self, parser):
        # self.PDBtags[33] REMARK
        # self.allLines
        #
        # only work for pdb, if cif it will be different.
        from MolKit.mmcifParser import MMCIFParser
        if isinstance(parser, MMCIFParser):
            # use symmetry from mmcif
            pass
        else:
            allLines = parser.allLines
            rem4 = [x for x in allLines if x[:18] == 'REMARK 350   BIOMT']
            lmatrix = {}
            for l in rem4:
                spl = l.split()
                symOpNum = int(spl[3])  # int(l[20:23]) #id of matrice
                # 1  1.000000  0.000000  0.000000        0.00000
                # id x y z x
                if symOpNum not in lmatrix:
                    lmatrix[symOpNum] = []
                symx = float(spl[4])  # float(l[23:33])
                symy = float(spl[5])  # float(l[33:43])
                symz = float(spl[6])  # float(l[43:53])
                tr = float(spl[7])  # float(l[53:])
                lmatrix[symOpNum].append([symx, symy, symz, tr])
                # ostr = "%5d\t%.3f\t%.3f\t%.3f\n" %(symOpNum, symx, symy, symz)
                # fptr.write(ostr)
                # ctr += 1
                # print "%5d\t%.3f\t%.3f\t%.3f\n" %(symOpNum, symx, symy, symz)
        return lmatrix

        # ===============================================================================

    # extra function
    # ===============================================================================
    def getHBBase(self, res1, res2, uniq=False):
        if uniq:
            ats = {"A": "N1", "T": "N3", "G": "N1", "C": "N3", "R": "N3"}  # R is for CBR
        else:
            ats = {"A": "N6,N1", "T": "O4,N3", "G": "N1,N2,O6", "C": "N3,O2,N4", "R": "N3,O2,N4"}  # R is for CBR
        ats1 = res1.atoms.get(ats[res1.type[-1]])
        ats2 = res2.atoms.get(ats[res2.type[-1]])
        return ats1, ats2

    def getDNAHbonds(self, nodes, uniq=False):
        # nodes should be the two dna chains
        # HBonds DNA
        # G=>N1,N2,O6 N3,N4,O2<=C
        # O6-N4
        # N1-N3
        # N2-O2
        # T=>O4,N3 N6,N1<=A    A
        # O4-N6
        # N3-N1
        pairs = {"A": "T", "G": "C", "T": "A", "C": "G", "R": "G"}
        hbonds_list = []  # will be (at1,at2)
        # need one cylinder per hbnonds
        if not isinstance(nodes, ChainSet):
            print("not chainset")
            return
        if not nodes[0].isDna() or not nodes[1].isDna():
            print("not dna")
            return
        # should not have water residues
        for i, res in enumerate(nodes[0].residues):  #
            paired = nodes[1].residues[-i - 1]
            # check the paired
            #            print(res,res.type,paired,paired.type,pairs[res.type[-1]],paired.type[-1])
            if pairs[res.type[-1]] != paired.type[-1]:
                if res.type[-1] != "R" and paired.type[-1] != "R":
                    return
            atmspair = self.getHBBase(res, paired, uniq=uniq)
            hbonds_list.append(atmspair)
        return hbonds_list

    def displayDNAHbonds(self, listHBatms, instance=None, bicyl=False, pb=False,
                         res=32, size=0.25, sc=2., hiera='perRes'):
        # need a root parent
        # need base shape
        sc = self.helper.getCurrentScene()
        instance = None
        mol = listHBatms[0][0][0].top
        ghbonds = []
        if instance == None:
            # create mesh_baseBond
            parent = self.helper.newEmpty(mol.name + "_b_hbonds")
            self.helper.addObjectToScene(sc, parent,
                                         parent=mol.geomContainer.masterGeom.obj)
            if self.host != "c4d":
                self.helper.toggleDisplay(parent, False)
            instance = self.helper.newEmpty(mol.name + "_b_hbonds_shape")
            self.helper.addObjectToScene(sc, instance, parent=parent)
            cyl = self.helper.Cylinder(mol.name + "_b_hbonds_o", res=res, radius=0.5)
            self.helper.reParent(cyl[0], instance)
            #            self.helper.toggleDisplay(cyl,display=False)
            if self.host.find("blender") != -1:
                baseCyl = self.helper.Cylinder("baseCyl", radius=0.5, length=1., res=res)
                self.helper.toggleDisplay(baseCyl, display=False)
                instance = self.helper.getMesh("mesh_" + mol.name + "_b_hbonds_o")
            elif self.host == "maya":
                #                self.helper.toggleDisplay(cyl,display=False)
                instance = cyl
            elif self.host == "c4d":
                instance = parent

        parent = self.helper.getObject(mol.name + "_hbonds")
        if parent is None:
            parent = self.helper.newEmpty(mol.name + "_hbonds")
            self.helper.addObjectToScene(sc, parent,
                                         parent=mol.geomContainer.masterGeom.obj)
        oneparent = True
        if pb:
            self._resetProgressBar()
            self._progressBar(0., 'creating bonds sticks')
        for paired in listHBatms:
            atms1 = paired[0]
            atms2 = paired[1]
            for atm1, atm2 in zip(atms1, atms2):
                if bicyl:
                    bond = self.biStick(atm1, atm2,
                                        hiera, instance, parent=parent)
                else:
                    bond = self.oneStick(atm1, atm2,
                                         hiera, instance, parent=parent)
                ghbonds.append(bond)
        return [ghbonds, instance]

    def displayStruts(self, node, instance=None, bicyl=False, pb=False,
                      res=32, size=0.25, sc=2., hiera='perRes'):
        # need a root parent
        # need base shape
        # node need to be atoms..
        if not isinstance(node, AtomSet): node = node.findType(Atom)
        hbats = AtomSet(node.get(lambda x: hasattr(x, 'struts')))
        #        print((hbats),hbats)
        mol = node[0].top
        sc = self.helper.getCurrentScene()
        instance = None
        gstruts = []
        if instance == None:
            # create mesh_baseBond
            parent = self.helper.newEmpty(mol.name + "_b_struts")
            self.helper.addObjectToScene(sc, parent,
                                         parent=mol.geomContainer.masterGeom.obj)
            if self.host != "c4d":
                self.helper.toggleDisplay(parent, False)
            instance = self.helper.newEmpty(mol.name + "_b_struts_shape")
            self.helper.addObjectToScene(sc, instance, parent=parent)
            cyl = self.helper.Cylinder(mol.name + "_b_struts_o", res=res, radius=0.5)
            self.helper.reParent(cyl[0], instance)
            #            self.helper.toggleDisplay(cyl,display=False)
            if self.host.find("blender") != -1:
                baseCyl = self.helper.Cylinder("baseCyl", radius=0.5, length=1., res=res)
                self.helper.toggleDisplay(baseCyl, display=False)
                instance = self.helper.getMesh("mesh_" + mol.name + "_b_struts_o")
            elif self.host == "maya":
                #                self.helper.toggleDisplay(cyl,display=False)
                instance = cyl
            elif self.host == "c4d":
                instance = parent

        parent = self.helper.getObject(mol.name + "_struts")
        if parent is None:
            parent = self.helper.newEmpty(mol.name + "_struts")
            self.helper.addObjectToScene(sc, parent,
                                         parent=mol.geomContainer.masterGeom.obj)
        oneparent = True
        if pb:
            self._resetProgressBar()
            self._progressBar(0., 'creating struts sticks')
        for struts in hbats:
            for strut in struts.struts:
                atm1 = strut.donAt
                atm2 = strut.accAt
                # for atm1,atm2 in zip(atms1,atms2):
                if bicyl:
                    bond = self.biStick(atm1, atm2,
                                        hiera, instance, parent=parent)
                else:
                    bond = self.oneStick(atm1, atm2,
                                         hiera, instance, parent=parent)
                gstruts.append(bond)
        return [gstruts, instance]

    def getDomains(self, mol, method="pdp"):
        # 'SCOP', 'CATH', 'dp' and 'pdp'
        try:
            import SOAPpy
        except:
            print ("install SOAPpy")
            setattr(mol, "hasDomains", False)
            return -1
        try:
            server = SOAPpy.SOAPProxy("http://www.pdb.org/pdb/services/pdbws")
        except:
            print ("problem connection")
            setattr(mol, "hasDomains", False)
            return -2
        molname = mol.name
        chains = mol.chains.name
        strchains = ""
        for c in chains:
            strchains += c + ","
        #        print molname,strchains[:-1],method
        res = server.getDomainFragments(molname[0:4], strchains[:-1], method)
        setattr(mol, "hasDomains", True)
        setattr(mol, "domains", res)
        for ats in mol.allAtoms:
            r = ats.parent
            ats.domainFragmentNumber = self.getResDomain(r, res)
        return 0

    def getResDomain(self, r, domains):
        for d in domains:
            if r.parent.name == d.methodChainId:
                if int(r.number) >= int(d.methodStart) and int(r.number) <= int(d.methodEnd):
                    return d.domainFragmentNumber
        return 0

    def getDomainsResiduesCoords(self, mol):
        lres = self.getDomainsResidues(mol)
        lcoords = []
        for lr in lres:
            coord = []
            for r in lr:
                coord.extend(r.atoms.coords)
            lcoords.append(coord)
        return lcoords

    def getDomainsResidues(self, mol):
        if not mol: return
        if not len(mol.domains): return
        domainResidues = []
        for d in mol.domains:
            st = d.methodStart
            end = d.methodEnd
            ch = mol.chains.get(d.methodChainId)
            lres = [r for r in ch.residues if int(r.number) >= int(d.methodStart) and int(r.number) <= int(d.methodEnd)]
            # lres = ch.residues.get(st+"-"+end)
            #            if not len(lres):
            #                print ch,d.methodChainId
            #                print st,end,st+"-"+end
            #                print  ch.residues.get(st+"-"+end)
            #                print d
            domainResidues.append(lres)
        return domainResidues
