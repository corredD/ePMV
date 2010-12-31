# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 08:38:56 2010

@author: -
"""
import os

from pyubic import uiadaptor

#define the general parameter and function for gui
from ePMV import comput_util as C
#from ePMV.uiAdaptor import uiAdaptor

import ePMV

class ParameterModeller(uiadaptor):
    def setup(self,epmv,id=1005):
        self.subdialog = True
        self.title = "Modeller"
        self.epmv = epmv
        witdh=350
        if id is not None :
            id=id
        else:
            id = self.bid
        self.LABEL_ID = {}

        self.NUMBERS = {
        "miniIterMax": self._addElemt(id=id,name="Max iteration",width=50,height=10,
                                            action=None,type="inputInt",
                                            icon=None,
                                            value = 1000,
                                            variable=self.addVariable("int",0),
                                            mini=0,maxi=100000,step=1),
        "mdIterMax":self._addElemt(id=id+1,name="Max iteration",width=50,height=10,
                                            action=None,type="inputInt",
                                            icon=None,
                                            value = 1000,
                                            variable=self.addVariable("int",0),
                                            mini=0,maxi=100000,step=1),
        "mdTemp":self._addElemt(id=id+2,name="Temperature",width=50,height=10,
                                            action=None,type="inputInt",
                                            icon=None,
                                            value = 300,
                                            variable=self.addVariable("int",0),
                                            mini=-100,maxi=1000,step=1),
        "rtstep":self._addElemt(id=id+3,name="number of steps",width=100,height=10,
                                            action=self.setRealTimeStep,
                                            type="inputInt",
                                            icon=None,
                                            value = 2,
                                            variable=self.addVariable("int",0),
                                            mini=0,maxi=100,step=1)
                        }
        id = id + len(self.NUMBERS) 
        
        self.LABEL_ID["miniIterMax"]=self._addElemt(id=id,
                    label=self.NUMBERS["miniIterMax"]["name"],
                    width=80)
        self.LABEL_ID["mdIterMax"]=self._addElemt(id=id+1,
                    label=self.NUMBERS["mdIterMax"]["name"],
                    width=80)
        self.LABEL_ID["mdTemp"]=self._addElemt(id=id+2,
                    label=self.NUMBERS["mdTemp"]["name"],
                    width=80)        
        self.LABEL_ID["rtstep"]=self._addElemt(id=id+3,
                    label=self.NUMBERS["rtstep"]["name"],
                    width=80)
        id = id + 4
        
        self.BTN = {
        "mini":self._addElemt(id=id,name="Minimize",width=50,height=10,
                              label = 'Minimize options',
                         action=self.epmv.gui.modellerOptimize,type="button"),
        "md":self._addElemt(id=id+1,name="run MD",width=50,height=10,
                            label = 'Molecular Dynamic options',
                         action=self.epmv.gui.modellerMD,type="button"),
        "cancel":self._addElemt(id=id+2,name="Cancel",width=50,height=10,
                         action=None,type="button"),
        "update coordinate":self._addElemt(id=id+3,name="Update coordinates",width=100,height=10,
                         action=self.updateCoord,type="button")
                         }
        id = id + len(self.BTN)
        
        self.LABEL_ID["mini"]=self._addElemt(id=id,
                    label=self.BTN["mini"]["label"],
                    width=80)        
        self.LABEL_ID["md"]=self._addElemt(id=id+1,
                    label=self.BTN["md"]["label"],
                    width=80)
        id = id + 2
        
        self.CHECKBOXS ={
        "store":self._addElemt(id=id,name="store",width=100,height=10,
                                              action=self.setStoring,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0)),
        "real-time":self._addElemt(id=id+1,name="real-time",width=100,height=10,
                                              action=self.setRealTime,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
                        }
        id = id + len(self.CHECKBOXS)
        
        self.rtType = ["mini","md"]
        self.sObject = ["cpk","lines","bones","spline"]
        self.COMB_BOX = {"sobject":self._addElemt(id=id,name="Object",
                                    value=self.sObject,
                                    width=60,height=10,action=self.setObjectSynchrone,
                                    variable=self.addVariable("int",0),
                                    type="pullMenu",),
                         "rtType":self._addElemt(id=id+1,name="rtType",
                                    value=self.rtType,
                                    width=60,height=10,action=self.setRToptimzeType,
                                    variable=self.addVariable("int",0),
                                    type="pullMenu",)}
        id = id + len(self.COMB_BOX)

        self.setupLayout()
        return True

    def setupLayout(self):
        self._layout=[]
        self._layout.append([self.CHECKBOXS["store"],])
        self._layout.append([self.CHECKBOXS["real-time"],self.COMB_BOX["rtType"]])
        self._layout.append([self.LABEL_ID["rtstep"],self.NUMBERS["rtstep"]])
        self._layout.append([self.BTN["update coordinate"],self.COMB_BOX["sobject"]])
        self._layout.append([self.LABEL_ID["mini"],])
        self._layout.append([self.LABEL_ID["miniIterMax"],self.NUMBERS["miniIterMax"]])
        self._layout.append([self.BTN["mini"],])
        self._layout.append([self.LABEL_ID["md"],])
        self._layout.append([self.LABEL_ID["mdIterMax"],self.NUMBERS["mdIterMax"]])
        self._layout.append([self.LABEL_ID["mdTemp"],self.NUMBERS["mdTemp"]])
        self._layout.append([self.BTN["md"],])
#        return True
 
    def CreateLayout(self):
        self._createLayout()
#        self.restorePreferences()
        return True
        
    #overwrite RT checkbox action
    def setRealTime(self,*args):
        mol = self.epmv.gui.current_mol
        mol.pmvaction.temp = self.getLong(self.NUMBERS["mdTemp"])
        mol.pmvaction.realtime = self.getBool(self.CHECKBOXS['real-time'])
        
    def setRealTimeStep(self,*args):
        mol = self.epmv.gui.current_mol
        mol.pmvaction.mdstep = self.getLong(self.NUMBERS['rtstep'])

    def setStoring(self,*args):
        mol = self.epmv.gui.current_mol
        mol.pmvaction.store = self.getBool(self.CHECKBOXS['store'])

    def setObjectSynchrone(self,*args):
        mol = self.epmv.gui.current_mol
        mol.pmvaction.sObject = self.sObject[self.getLong(self.COMB_BOX["sobject"])]

    def setRToptimzeType(self,*args):
        mol = self.epmv.gui.current_mol
        rtype= self.rtType[self.getLong(self.COMB_BOX["rtType"])]
        if mol.pmvaction.rtType != rtype :
            mol.pmvaction.rtType = rtype
            #need to update the optimizer ie delete and create a new one
            mol.pmvaction.resetOptimizer()

    def updateCoord(self,*args):
        if hasattr(self.epmv,'gui'):
            mol = self.epmv.gui.current_mol
            if hasattr(mol,'pmvaction'):
                self.epmv.helper.updateMolAtomCoord(mol,mol.pmvaction.idConf,types=mol.pmvaction.sObject)
                mol.pmvaction.updateModellerCoord(mol.pmvaction.idConf,mol.mdl)       

    def doIt(self,*args):
        pass
        
    def Command(self,*args):
#        print args
        self._command(args)
        return True

class ParameterScoringGui:
    def __init__(self,epmv=None):
        self.epmv = epmv
        id=1005
        self.BTN = {"rec":{"id":id,"name":"Browse",'width':50,"height":10,
                           "action":None},
                    "lig":{"id":id+1,"name":"Browse",'width':50,"height":10,
                           "action":None},
                    "ok":{"id":id+2,"name":"Add Scorer",'width':50,"height":10,
                          "action":self.setup},
                    "gScore":{"id":id+3,"name":"Get Score",'width':50,"height":10,
                          "action":self.getScore}  
                    }
        id = id + len(self.BTN)
        self.TXT = {"rec":{"id":id,"name":"Receptor",'width':50,
                           "height":10,"action":None},
                    "lig":{"id":id+1,"name":"ligand",'width':50,
                           "height":10,"action":None}
                    }
        id = id + len(self.TXT)

        self.COMB_BOX = {"score":{"id":id,"name":"type of score","width":60,
                                  "height":10,"action":self.setScorer},
                         "scorer":{"id":id+1,"name":"available scorer","width":60,
                                   "height":10,"action":self.setCurrentScorer},
                         }
        id = id + len(self.COMB_BOX)
        self.scorertype = ['PyPairWise','ad3Score','ad4Score']
        if C.cAD : #cAutodock is available
            self.scorertype.append('c_ad3Score')
            self.scorertype.append('PairWise')
        self.getScorerAvailable()
        self.CHECKBOXS ={"store":{"id":id,"name":"store",'width':100,
                                  "height":10,"action":None},
                        "displayLabel":{"id":id+1,"name":"display Label",'width':100,
                                    "height":10,"action":None},
                        "colorRec":{"id":id+2,"name":"color Rec",'width':100,
                                    "height":10,"action":None},
                        "colorLig":{"id":id+3,"name":"color Lig",'width':100,
                                    "height":10,"action":None},
                        "realtime":{"id":id+4,"name":"real time",'width':100,
                                    "height":10,"action":self.setRealtime}
                                    }
        id = id + len(self.CHECKBOXS)
        return True

    def getScorerAvailable(self):
        self.scoreravailable = []
        if hasattr(self.epmv.mv,'energy'):
            self.scoreravailable = self.epmv.mv.energy.data.keys()

    def getScore(self):
        if hasattr(self.epmv.mv,'energy'):
            self.epmv.helper.get_nrg_score(self.epmv.mv.energy)

          

class Parameter_epmvGUI(uiadaptor):
    def setup(self,epmv,id=None):
        self.subdialog = True
        self.title = "Preferences"
        self.epmv = epmv
        witdh=350
        if id is not None :
            id=id
        else:
            id = self.bid
        #need to split in epmv options and gui options - >guiClass?
        self.EPMVOPTIONS = {}
        for key in self.epmv.keywords : 
            if self.epmv.keywords[key] is not None and key != "synchro_ratio" \
                and key != "synchro_timeline":
                self.EPMVOPTIONS[key] = self._addElemt(id=id,
                                            name=self.epmv.keywords[key]["name"],
                                            width=witdh,height=10,
                                            action=None,type=self.epmv.keywords[key]["type"],
                                            icon=None,
#                                            value = self.epmv.keywords[key]["value"],
                                            variable=self.addVariable("int",0))
                id = id +1
        #special case of synchro_ratio
        self.SRATIO=[[self._addElemt(id=id,
                            name=self.epmv.keywords["synchro_timeline"]["name"],
                            width=witdh,height=10,
                            action=None,type=self.epmv.keywords["synchro_timeline"]["type"],
                            icon=None,
                            variable=self.addVariable("int",0)),],
                     [self._addElemt(id=id+1,
                                            name=self.epmv.keywords["synchro_ratio"][0]["name"],
                                            width=80,height=10,
                                            action=None,
                                            type=self.epmv.keywords["synchro_ratio"][0]["type"],
                                            icon=None,
                                            value=self.epmv.keywords["synchro_ratio"][0]["value"],
                                            mini=self.epmv.keywords["synchro_ratio"][0]["mini"],
                                            maxi=self.epmv.keywords["synchro_ratio"][0]["maxi"],
                                            variable=self.addVariable("int",0)),
                    self._addElemt(id=id+2,
                    label=self.epmv.keywords["synchro_ratio"][0]["name"],
                    width=120),],
                    [self._addElemt(id=id+3,
                                            name=self.epmv.keywords["synchro_ratio"][1]["name"],
                                            width=80,height=10,
                                            action=None,
                                            type=self.epmv.keywords["synchro_ratio"][1]["type"],
                                            icon=None,
                                            value=self.epmv.keywords["synchro_ratio"][1]["value"],
                                            mini=self.epmv.keywords["synchro_ratio"][1]["mini"],
                                            maxi=self.epmv.keywords["synchro_ratio"][1]["maxi"],                                            
                                            variable=self.addVariable("int",0)),
                    self._addElemt(id=id+4,
                    label=self.epmv.keywords["synchro_ratio"][1]["name"],
                    width=120)]]
        id = id +5
        self.BTN = self._addElemt(id=id,name="OK",action=self.SetPreferences,width=50,
                          type="button")
        id = id + 1
        self.setupLayout()
#        self.restorePreferences()
        return True

    def setupLayout(self):
        self._layout = []
        for key in self.EPMVOPTIONS:
            self._layout.append([self.EPMVOPTIONS[key],])
        self._layout.append(self.SRATIO[0])
        self._layout.append(self.SRATIO[1])
        self._layout.append(self.SRATIO[2])
        self._layout.append([self.BTN,])
 
    def CreateLayout(self):
        self._createLayout()
        self.restorePreferences()
        return True
        
    def SetPreferences(self,*args):
        print args
        for key in self.EPMVOPTIONS:
            setattr(self.epmv,key,self.getBool(self.EPMVOPTIONS[key]))
        self.epmv.synchro_timeline = self.getBool(self.SRATIO[0][0])
        self.epmv.synchro_ratio[0] = self.getLong(self.SRATIO[1][0])
        self.epmv.synchro_ratio[1] = self.getLong(self.SRATIO[2][0])
        if self.epmv.useModeller and self.epmv._modeller:
            self.epmv.center_mol = False
            self.epmv.center_grid = False
            if self.epmv.env is None:
                from ePMV.extension.Modeller.pmvAction import setupENV
                #setup Modeller
                self.epmv.env = setupENV()
        #if self.epmv.synchro_realtime:
        self.epmv.synchronize()
#        #self.AskClose()
#        if self.epmv.gui._depthQ :
#            self.epmv.helper.create_environment('depthQ',distance = 30.)
#        else :
#            obj=self.epmv.helper.getObject('depthQ')
#            if obj is not None :
#                self.epmv.helper.toggleDisplay(obj,False)
        self.close()
        
    def restorePreferences(self):
        for key in self.EPMVOPTIONS:
            self.setBool(self.EPMVOPTIONS[key],getattr(self.epmv,key))
        self.setBool(self.SRATIO[0][0],self.epmv.synchro_timeline)
        self.setLong(self.SRATIO[1][0],self.epmv.synchro_ratio[0])
        self.setLong(self.SRATIO[2][0],self.epmv.synchro_ratio[0])
#        if self.epmv.gui._modeller :
#            self.SetBool(self.OPTIONS['modeller']["id"],self.epmv.gui._useModeller)
        
    def Command(self,*args):
#        print args
        self._command(args)
        return True


#should be called uiDialog, and uiSubDialog ?
class epmvGui(uiadaptor):
    #TODO complete the command callback
    #
    restored=False
    status = 0
    link = 0
    nF=1000
    __version__="0.2.0a"
    __about__="ePMV v"+__version__+"\n"
    __about__+="""\
ePMV by Ludovic Autin,Graham Jonhson,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.
"""
    __url__ = ["http://epmv.scripps.edu",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt',
           'http://epmv.scripps.edu/documentation/citations-informations',]

    host=""
    bid=1
    
    def setup(self,epmv=None,rep="epmv",mglroot="",host=''):        
        if not host :
            if not self.host:
                self.host = epmv.host 
        elif not self.host:
            self.host = host
#        print "selfdict ",self.__dict__
#        print dir(self)
        self.restored = False   
        if epmv is None:
            #try to restore
            print "try to restore"
            epmv = self._restore('mv',rep)
            print epmv
            if epmv is None:
                epmv = ePMV.epmv_start(self.host,debug=0)
                if mglroot :
                    epmv.mglroot = mglroot
                else :
                    epmv.mglroot = ""
                epmv.gui = self
                epmv.initOption()
            else :
                self.restored = True
            self._store('mv',{epmv.rep:epmv})
        self.epmv = epmv
        self.mv = epmv.mv
        self.funcColor = [self.mv.colorByAtomType,
                          self.mv.colorAtomsUsingDG,
                          self.mv.colorByResidueType,
                          self.mv.colorResiduesUsingShapely,
                          self.mv.colorBySecondaryStructure,
                          self.mv.colorByChains,
                          self.mv.color,
                          self.mv.colorByProperty]
#        print self.funcColor
        self.colSchem=['Atoms using CPK',
               'AtomsDG (polarity/charge)',
               'Per residue',
               'Per residue shapely',
               'Secondary Structure',
               'Chains',
               'Custom color',
               'Rainbow from N to C',
               'Temperature Factor',
               'sas area']

        #before creating the menu check the extensiosn
        #self.checkExtension()
        #as the recent File
        self.title = "ePMV"
        self.y = 620
        self.epmv.setupMaterials()
        self.epmv.checkExtension()
        self.initWidget()
        self.setupLayout()

    def CreateLayout(self):
        self._createLayout()
        if self.restored :
            for mol in self.mv.Mols:
                print "restore ",mol.name
                self.addItemToPMenu(self.COMB_BOX["mol"],mol.name)
                for dataname in self.mv.iMolData[mol.name] :
                    print "restore dataname ",dataname
                    self.addItemToPMenu(self.COMB_BOX["dat"],dataname)
                    self.current_traj = self.mv.iTraj[1]
#                self.buttonLoad(None,mname=mol.name)
#                self.firstmol = False
#                #need to restore the data
#                for dataname in self.mv.iMolData[mol.name] :
#                    print "dataname ",dataname               
#                    self.buttonLoadData(None,trajname=dataname,molname=mol.name)              
#                #need to restore the selection
#                if mol.name in self.mv.MolSelection.keys():
#                    self.add_Selection(n=mol.name)
#                #for selname in self.mv.MolSelection[mol.name].keys() :
                #    self.addChildToMolMenu(selname)
            self.restored = False                  
        return True

    def Command(self,*args):
#        print args
        self._command(args)
        return True

    def initWidget(self,id=None):
        if id is not None :
            id=id
        else:
            id = self.bid
        self.iconsdir = self.epmv.mglroot+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+\
                        os.sep+"images"+os.sep+"icons"+os.sep
        self.menuorder = ["File","Edit","Extensions","Help"]
        #submenu recentFile.
        self.submenu= None
        if self.mv.recentFiles.categories.has_key("Documents"):
            self.submenu={}
            for i,r in enumerate(self.mv.recentFiles.categories["Documents"]):
                if r[1] == "readMolecule" :
                    #id*(i+2)
                    self.submenu[str(i)]=self._addElemt(id=i, 
                                            name=r[0],
                                            action=self.loadRecentFile)
                    id = id +1
        self._menu = self.MENU_ID = {"File":
                      [self._addElemt(id=id, name="Recent Files",action=None,sub=self.submenu),
                      self._addElemt(id=id+1, name="Open PDB",action=self.browsePDB),#self.buttonLoad},
                      self._addElemt(id=id+2, name="Open Data",action=self.browseDATA)],#self.buttonLoadData
                       "Edit" :
                      [self._addElemt(id=id+3, name="Options",action=self.drawPreferences)],#self.drawPreferences}],
#                      [{"id": id+3, "name":"Camera&c&","action":self.optionCam},
#                       {"id": id+4, "name":"Light&c&","action":self.optionLight},
#                       {"id": id+5, "name":"CloudsPoints&c&","action":self.optionPC},
#                       {"id": id+6, "name":"BiCylinders&c&","action":self.optionCyl}],
                       "Extensions" : [
                       self._addElemt(id=id+4, name="PyAutoDock",action=None)#self.drawPyAutoDock}
                       ],
                       "Help" : 
                      [self._addElemt(id=id+5, name="About ePMV",action=self.drawAbout),#self.drawAbout},
                       self._addElemt(id=id+6, name="ePMV documentation",action=self.launchBrowser),#self.launchBrowser},
                       self._addElemt(id=id+7, name="Check for Update",action=None),#self.check_update},
                       self._addElemt(id=id+8, name="Citation Informations",action=self.citationInformation),#self.citationInformation},
                      ],
                       }
        id = id + 9
        if self.epmv._AF :
            self.MENU_ID["Extensions"].append(self._addElemt(id=id, name="AutoFill",
                                                action=None))#self.launchAFgui})
            id = id + 1 
        if self.epmv._AR :
            self.MENU_ID["Extensions"].append(self._addElemt(id=id, name="ARViewer",
                                                action=None))#self.launchARgui})
            id = id + 1 
        if self.epmv._modeller:            
            self.MENU_ID["Extensions"].append(self._addElemt(id=id, name="Modeller",
                                                action=self.drawModellerGUI))#self.modellerGUI})
            id = id + 1
        self.MENU_ID["Extensions"].append(self._addElemt(id=id, name="Add an Extension",
                                                action=self.addExtensionGUI))#self.addExtensionGUI})
        id = id + 1
        self.LABEL_ID = []
        self.LABEL_ID.append(self._addElemt(id=id,
                    label="to a PDB file OR enter a 4 digit ID (e.g. 1crn):",
                    width=120))
        self.LABEL_ID.append(self._addElemt(id=id+1,label="",width=1))
        self.LABEL_ID.append(self._addElemt(id=id+2,
                    label="Current selection :",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+3,
                    label="Add selection set using string or",width=120))
        self.LABEL_ID.append(self._addElemt(id=id+4,label="Color scheme:",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+5,label="to load a Data file",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+6,label="to Current Selection and play below:",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+7,label="PMV-Python scripts/commands",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+8,label="Molecular Representations",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+9,label="Apply",width=20))
        self.LABEL_ID.append(self._addElemt(id=id+10,label="a Selection Set",width=50))
        self.LABEL_ID.append(self._addElemt(id=id+11,label="atoms in the Selection Set",width=120))
        self.LABEL_ID.append(self._addElemt(id=id+12,label="or",width=10))
        self.LABEL_ID.append(self._addElemt(id=id+13, label="or",width=10))
        self.LABEL_ID.append(self._addElemt(id=id+14,label=":",width=10))
        id = id + len(self.LABEL_ID)
        
        self.LABEL_VERSION = self._addElemt(id=id,label='welcome to ePMV '+self.__version__,width=50)
        id = id + 1
        
        self.pdbid = self.addVariable("str","1crn")
        self.EDIT_TEXT = self._addElemt(id=id,name="pdbId",action=None,width=120,
                          value="1crn",type="inputStr",variable=self.pdbid)
        id = id + 1
                
        self.LOAD_BTN = self._addElemt(id=id,name="Browse",width=40,height=10,
                         action=self.browsePDB,type="button")#self.buttonBrowse
        id = id + 1
        self.FETCH_BTN = self._addElemt(id=id,name="Fetch",width=30,height=10,
                         action=self.fetchPDB,type="button")#self.buttonLoad}
        id = id + 1
        self.DATA_BTN = self._addElemt(id=id,name="Browse",width=40,height=10,
                         action=self.browseDATA,type="button")#self.buttonLoadData}
        id = id + 1
        self.PMV_BTN = self._addElemt(id=id,name="Exec",width=80,height=10,
                         action=self.execPmvComds,type="button")#self.execPmvComds}
        id = id + 1
        self.KEY_BTN= {"id":id,"name":"store key-frame",'width':80,"height":10,
                         "action":None}
        id = id + 1
#        self.DEL_BTN= self._addElemt(id=id,name="Delete",width=80,height=10,
#                         action=self.deleteMol,type="button")
#        id = id + 1
#        print "id del button", id-1

        #values and variable definition
        self.datatype=['e.g.','Trajectories:','  .trj','  .xtc','VolumeGrids:']
        DataSupported = '\.mrc$|\.MRC$|\.cns$|\.xplo*r*$|\.ccp4*$|\.grd$|\.fld$|\.map$|\.omap$|\.brix$|\.dsn6$|\.dn6$|\.rawiv$|\.d*e*l*phi$|\.uhbd$|\.dx$|\.spi$'
        DataSupported=DataSupported.replace("\\","  ").replace("$","").split("|")
        self.datatype.extend(DataSupported)
        
        self.presettype=['available presets:','  Lines','  Liccorice','  SpaceFilling',
                         '  Ball+Sticks','  RibbonProtein+StickLigand',
                         '  RibbonProtein+CPKligand','  xray','  Custom',
                         '  Save Custom As...']
        self._preset = self.addVariable("int",1)
        
        self.keyword = ['keywords:','  backbone','  sidechain','  chain','  picked']
        from MolKit.protein import ResidueSetSelector
        kw=map(lambda x:"  "+x,ResidueSetSelector.residueList.keys())
        self.keyword.extend(kw)
        self._keyword=self.addVariable("int",1)
        
        self.scriptliste = ['Open:',
                            'pymol_demo',
                            'interactive_docking',
                            'colorbyAPBS',
                            'demo1',
                            'user_script']
        self.scriptsave = ['Save','Save as']
        self._eOscript = self.addVariable("int",1)
        self._eSscript = self.addVariable("int",1)
        
        self.editselection = ['Save set','Rename set','Delete set']
        self._eSelection = self.addVariable("int",1)
        
        self.pdbtype=['PDB','TMPDB','OPM','CIF','PQS']
        self._pdbtype=self.addVariable("int",1)
        
        self._currentmol=self.addVariable("int",1)
        self._col=self.addVariable("int",1)
        self._dat=self.addVariable("int",1)
        
        self.COMB_BOX = {"mol":self._addElemt(id=id,name="Current",value=["None"],
                                    width=60,height=10,action=None,variable=self._currentmol,
                                    type="pullMenu",),#self.update},#self.setCurMol
                         "col":self._addElemt(id=id+1,name="Color",value=self.colSchem,
                                    width=80,height=10,action=self.color,variable=self._col,
                                    type="pullMenu",),#self.color},
                         "dat":self._addElemt(id=id+2,name="Data",value=["None"],
                                    width=60,height=10,action=self.updateTraj,variable=self._dat,
                                    type="pullMenu",),#self.updateTraj},
                         "pdbtype":self._addElemt(id=id+3,name="Fecth",value=self.pdbtype,
                                    width=50,height=10,action=None,variable=self._pdbtype,
                                    type="pullMenu",),
                         "datatype":self._addElemt(id=id+4,name="DataTypes",value=self.datatype,
                                    width=60,height=10,action=None,variable=self.addVariable("int",1),
                                    type="pullMenu",),
                         "preset":self._addElemt(id=id+5,name="Preset",value=self.presettype,
                                    width=80,height=10,action=self.drawPreset,variable=self._preset,
                                    type="pullMenu",),#self.drawPreset},
                         "keyword":self._addElemt(id=id+6,name="Keyword",value=self.keyword,
                                    width=80,height=10,action=self.setKeywordSel,variable=self._keyword,
                                    type="pullMenu",),#self.setKeywordSel},
                         "scriptO":self._addElemt(id=id+7,name="ScriptO",value=self.scriptliste,
                                    width=80,height=10,action=self.set_ePMVScript,variable=self._eOscript,
                                    type="pullMenu",),#self.set_ePMVScript},
                         "scriptS":self._addElemt(id=id+8,name="ScriptS",value=self.scriptsave,
                                    width=80,height=10,action=None,variable=self._eSscript,
                                    type="pullMenu",),#self.save_ePMVScript},
                         "selection":self._addElemt(id=id+9,name="Selection",value=self.editselection,
                                    width=80,height=10,action=None,variable=self._eSelection,
                                    type="pullMenu",),#elf.edit_Selection},
                         }
        id = id + len(self.COMB_BOX)

        deflt='(Mol:Ch:Rletter:Atom), eg "1CRN:A:ALA:CA", \
                or keywords: BACKBONE, SIDECHAINS, etc...'
        self.selid = self.addVariable("str",deflt)
        self.SELEDIT_TEXT = self._addElemt(id=id,name="selection",action=None,width=120,
                          value=deflt,type="inputStr",variable=self.selid)
        id = id+1

        self.SEL_BTN ={"add":self._addElemt(id=id,name="Save set",width=45,height=10,
                         action=None,type="button"),#self.add_Selection},
                        "rename":self._addElemt(id=id+1,name="Rename",width=45,height=10,
                         action=None,type="button"),#self.rename_Selection},
                        "deleteS":self._addElemt(id=id+2,name="Delete Set",width=45,height=10,
                         action=None,type="button"),#self.delete_Selection},
                        "deleteA":self._addElemt(id=id+3,name="Delete",width=45,height=10,
                         action=self.delete_Atom_Selection,type="button"),#self.delete_Atom_Selection}    
                        }
        id = id + len(self.SEL_BTN)
        #do we need check button for other representation? ie lineMesh,cloudMesh etc..
        self.CHECKBOXS ={"cpk":self._addElemt(id=id,name="Atoms",width=80,height=10,
                                              action=self.dsCPK,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0)),#self.displayCPK},
                         "bs":self._addElemt(id=id+1,name="Sticks",width=80,height=10,
                                             action=self.dsBS,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.displayBS},
                         "ss":self._addElemt(id=id+2,name="Ribbons",width=80,height=10,
                                             action=self.dsSS,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.displaySS},
                         "loft":self._addElemt(id=id+3,name="Loft",width=80,height=10,
                                               action=self.dsLoft,type="checkbox",icon=None,
                                               variable=self.addVariable("int",0)),#self.createLoft},
                         "arm":self._addElemt(id=id+4,name="Armature",width=80,height=10,
                                             action=self.dsBones,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.createArmature},
                         "spline":self._addElemt(id=id+5,name="Spline",width=80,height=10,
                                             action=self.dsSpline,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.createSpline},
                         "surf":self._addElemt(id=id+6,name="MSMSurf",width=80,height=10,
                                               action=self.dsMSMS,type="checkbox",icon=None,
                                               variable=self.addVariable("int",0)),#self.displaySurf},
                         "cms":self._addElemt(id=id+7,name="CoarseMolSurf",width=80,height=10,
                                             action=self.dsCMS,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.displayCoarseMS},
                         "meta":self._addElemt(id=id+8,name="Metaballs",width=80,height=10,
                                             action=self.dsMeta,type="checkbox",icon=None,
                                             variable=self.addVariable("int",0)),#self.displayMetaB}
                         }
        id = id + len(self.CHECKBOXS)
       
        #need a variable for each one
        #no label for theses
        #do we need slider button for other representation? ie metaball?/loft etc..
        self.SLIDERS = {"cpk":self._addElemt(id=id,name="cpk_scale",width=80,height=10,
                                             action=self.dsCPK,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.01,maxi=5.,step=0.01),#self.displayCPK},
                        "bs_s":self._addElemt(id=id+1,name="bs_scale",width=80,height=10,
                                             action=self.dsBS,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01),#self.displayBS},
                        "bs_r":self._addElemt(id=id+2,name="bs_ratio",width=80,height=10,
                                             action=self.dsBS,type="sliders",
                                             variable=self.addVariable("float",1.5),
                                             mini=0.0,maxi=10.,step=0.01),#self.displayBS},
                        "surf":self._addElemt(id=id+3,name="probe",width=80,height=10,
                                              action=self.updateMSMS,type="sliders",
                                              variable=self.addVariable("float",1.5),
                                             mini=0.01,maxi=10.,step=0.01),#self.updateSurf},
                        "cmsI":self._addElemt(id=id+4,name="isovalue",width=80,height=10,
                                              action=self.updateCMS,type="sliders",
                                              variable=self.addVariable("float",7.1),
                                             mini=0.01,maxi=10.,step=0.01),#self.updateCMS},
                        "cmsR":self._addElemt(id=id+5,name="resolution",width=80,height=10,
                                              action=self.updateCMS,type="sliders",
                                              variable=self.addVariable("float",-0.3),
                                             mini=-5.,maxi=0.,step=0.01),#self.updateCoarseMS},
                        #"meta":{"id":id+8,"name":"MBalls",'width':15,"height":10,"action":self.displayMetaB}
                        "datS":self._addElemt(id=id+6,name="state",width=100,height=10,
                                              action=self.applyState,type="sliders",
                                              variable=self.addVariable("float",0.),
                                             mini=-10.,maxi=10.,step=0.01),#self.applyState},
                        #"datV":{"id":id+7,"name":"value",'width':15,"height":10,"action":self.applyValue},                        
                        }
        id = id + len(self.SLIDERS)            
        self.COLFIELD = self._addElemt(id=id,name="chooseCol",action=self.color,
                                       variable = self.addVariable("col",(0.,0.,0.)),
                                       type="color",width=30,height=15)#self.chooseCol}
        id = id + 1

        txt="""
        
print 'put your own commands here'
print 'with self = PMV instance, and epmv as ePMV'
        """   
        self._script = self.addVariable("str",txt)
        self.SCRIPT_TEXT = self._addElemt(id=id,name="epmvScript",action=None,width=100,
                          value=txt,type="inputStrArea",variable=self._script,height=200)
        id = id + 1
        bannerfile = self.epmv.mglroot+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+\
                        os.sep+"images"+os.sep+"banner.jpg"
        self.BANNER = self._addElemt(id=id,name="banner",value=bannerfile,type="image")
        id = id + 1
        self.pd = ParameterModeller()
        self.pd.setup(self.epmv)
#        self.argui = ParameterARViewer()
#        self.ad=ParameterScoring()
        self.options = Parameter_epmvGUI()
        self.options.setup(self.epmv)
    
    def setupLayout(self):
        #epmv layout:
        #first is the Menu / last as in blender self.MENU_ID did by the adaptor
        #then is the pdb browse/fetch buttons
        #Load Molecule
        #line1  
        #need to reset the layout for restore purpose
        self._layout = []
        self._layout.append([self.LOAD_BTN,self.LABEL_ID[0],self.LABEL_ID[1]])
        #line2
        self._layout.append([self.EDIT_TEXT,self.COMB_BOX["pdbtype"],self.FETCH_BTN])        
        #line3
        self._layout.append([self.LABEL_ID[2],self.COMB_BOX["mol"]])
        #DashBoard / Selection Display Options 
        #line4
        self._layout.append([self.LABEL_ID[3],self.COMB_BOX["keyword"]])
        #line5
        self._layout.append([self.SELEDIT_TEXT,self.COMB_BOX["selection"]])
        #line6
        self._layout.append([self.SEL_BTN["deleteA"],self.LABEL_ID[11]])
        #line7
        self._layout.append([self.LABEL_ID[8],self.COMB_BOX["preset"]])
        #line8 // Visual represnetation option CPK, MSMS etc...checkbox!
#        self._layout.append([self.LABEL_ID[8],self.COMB_BOX["preset"]])
        repLayout={ "0": [3,5],
                    "1":[self.CHECKBOXS["cpk"],self.CHECKBOXS["ss"],self.CHECKBOXS["surf"]],
                    "2":[self.SLIDERS["cpk"],self.CHECKBOXS["loft"],self.SLIDERS["surf"]],
                    "3":[self.CHECKBOXS["bs"],self.CHECKBOXS["arm"],self.CHECKBOXS["cms"]],
                    "4":[self.SLIDERS["bs_s"],self.CHECKBOXS["spline"],self.SLIDERS["cmsI"]],
                    "5":[self.SLIDERS["bs_r"],self.CHECKBOXS["meta"],self.SLIDERS["cmsR"]],
                    }
        self._layout.append(repLayout)
        #line9#color what is check as display     
        self._layout.append([self.LABEL_ID[4],self.COMB_BOX["col"],self.COLFIELD])
        #line10#data player
        self._layout.append([self.DATA_BTN,self.LABEL_ID[5],self.COMB_BOX["datatype"]])
        self._layout.append([self.LABEL_ID[9],self.COMB_BOX["dat"],self.LABEL_ID[6]])
        self._layout.append([self.SLIDERS["datS"],])
        #line10#script editor
        self._layout.append([self.LABEL_ID[7],self.COMB_BOX["scriptO"],self.COMB_BOX["scriptS"]])
        self._layout.append([self.SCRIPT_TEXT,])        
        self._layout.append([self.PMV_BTN,])
        #Version
        self._layout.append([self.LABEL_VERSION,])
        #Banner if we can
        self._layout.append([self.BANNER,])

    
    def getGeomActive(self,name):
        lgeomName=[]
        mname,mol,sel,selection = self.getDsInfo()
        #lookup moldisp
        for key in self.CHECKBOXS:
            if self.getBool(self.CHECKBOXS[key]):
                if key == "bs" : 
                    lgeomName.append('balls')
                    lgeomName.append('sticks')
                elif key == "ss":
                    lgeomName.append('secondarystructure')
                elif key == "cms":
                    sname='CoarseMS_'+str(mname)
                    lgeomName.append(sname)   
                elif key == "surf":
                    sname='MSMS-MOL'+str(mname)
                    if sel != mname :sname='MSMS-MOL'+str(selname) 
                    lgeomName.append(sname)
                elif key == "col":
                    continue
                else :
                    lgeomName.append(key)
        return lgeomName

    def getData(self,molname,adt=False):
#        if molname in self.mv.Mols.name : self.mv.hostApp.driver.duplicatemol=False
        self.mv.assignAtomsRadii(str(molname), united=0, log=0, overwrite=1)
        self.epmv._addMolecule(molname)
        #add a child to mol pop up menu which is the current selection puulDowmn menu
        
        self.addItemToPMenu(self.COMB_BOX["mol"],str(molname))
        mol = self.mv.getMolFromName(molname)
        if len(mol.allAtoms[0]._coords) > 1 or self.epmv.useModeller : 
            #need a test about trajectories...
            doit=True           
            if len(self.mv.iMolData[mol.name]) != 0 : #ok data
                for dataname in self.mv.iMolData[mol.name] : 
                    if dataname.find('xtc') != -1 : 
                        doit= False                             
            if doit : self.loadDATA(None,model=True,molname=molname,adt=adt)
        self.current_mol = mol

    def loadPDB(self,filename):
        if not filename : return
        molname=os.path.splitext(os.path.basename(filename))[0]
#        print molname
        #test the name lenght
        if len(molname) > 7 :
            self.drawError("Sorry, but the name of the given file is to long,\nand not suppported by Blender.\n Please rename it or load another file")
            return 0
#        if VERBOSE :print molname, self.Mols.name, (molname in self.Mols.name)
        name=filename
        adt=False
        ext = os.path.splitext(os.path.basename(name))[1]
#        print ext
        if ext == '.dlg' :#Autodock
            self.epmv.center_mol = False
            self.mv.readDLG(name,1,0) #addToPrevious,ask
            self.mv.showDLGstates(self.mv.Mols[-1])
            molname = self.mv.Mols[-1].name
            adt=True
#        if molname in self.mv.Mols.name : 
#            self.hostApp.driver.duplicatemol=True
#            if VERBOSE :print self.hostApp.driver.duplicatemol
        if self.epmv.useModeller and not adt :
            import modeller
            from modeller.scripts import complete_pdb
            mdl = complete_pdb(self.epmv.env, name)
            mdl.patch_ss()
            name = name.split(".pdb")[0]+"m.pdb"
            mdl.write(file=name)
        if not adt :
            self.mv.readMolecule(str(name))
            if self.epmv.useModeller :
                self.mv.Mols[-1].mdl=mdl
        molname = self.mv.Mols[-1].name
        molname=molname.replace(".","_")

        self.mv.Mols[-1].name=molname

        if len(molname) > 7 : 
            self.mv.Mols[-1].name=molname[0:6]
            molname = self.mv.Mols[-1].name
        self.epmv.testNumberOfAtoms(self.mv.Mols[-1])
        self.getData(self.mv.Mols[-1].name)
        self.updateViewer()

    def loadRecentFile(self,*args):
#        print "RF ",args, len(args)
        if len(args) == 1:
            if type(args[0]) is tuple :
                id = args[0][0] 
            else :
                id = args[0]
        elif len(args) == 2:
            if type(args[0]) is str :
                id = args[0]
            else :
                id = args[0][0]
        if self.submenu is not None :
            filename = self.submenu[str(id)]["name"]
            self.loadPDB(filename)

    def browsePDB(self,*args):
        #first need to call the ui fileDialog
        self.fileDialog(label="choose a file",callback=self.loadPDB)
        
    def fetchPDB(self,*args):
#        print args
        #get the text area    
        name = self.getString(self.EDIT_TEXT)
        #need to get the fetch Type
        type = self.pdbtype[self.getLong(self.COMB_BOX["pdbtype"])]
        if len(name) == 4 or len(name.split(".")[0]) == 4 :
#            print "PDB id, webdownload"
            molname=name.lower()
#                if molname in self.mv.Mols.name : self.mv.hostApp.driver.duplicatemol=True
            self.mv.fetch.db = type
            print self.epmv.forceFetch
            mol = self.mv.fetch(molname,f=self.epmv.forceFetch)           
            if mol is None :
                return True
            self.epmv.testNumberOfAtoms(mol)
            self.getData(self.mv.Mols[-1].name)
            self.updateViewer()
        else :
            print "enter a Valid "+type+" id Code "
            
    def loadDATA(self,filename,model=False,trajname=None,molname=None,adt=False):
        if trajname == None :
            if model : 
                self.modelData(adt=adt)
                return True
            #filename=self.GetString(self.trajectoryfile)
            #if len(filename) == 0 :
            if filename is None :
                    return True
            dataname=os.path.splitext(os.path.basename(filename))[0]
            extension=os.path.splitext(os.path.basename(filename))[1] #.xtc,.trj,etc..
            if extension == '.xtc' or extension == '.dcd'  : self.gromacsTraj(file=filename)
            else : self.gridData(file=filename)
            #elif extension == '.map' : self.gridData_1(file=filename)
        else :
           print "restore ",trajname      
           if trajname.find(".model") != -1 or trajname.find(".dlg") != -1: #model conformation data
               self.modelData(dataname=trajname,molname=molname)          
           elif trajname.find("xtc") != -1 : #gromacs conformation data
               self.gromacsTraj(dataname=trajname,molname=molname)          
           else : #autodock map conformation data
               self.gridData(dataname=trajname,molname=molname)          
        #elif extension == '.trj' : self.amberTraj(filename)
        self.updateViewer()
        return True

    def browseDATA(self,*args):
        #first need to call the ui fileDialog
        self.fileDialog(label="choose a data file",callback=self.loadDATA)

    def modelData(self,dataname=None,molname=None,adt=False):
        if molname == None :
            val = self.getLong(self.COMB_BOX["mol"])
            vname = self.COMB_BOX["mol"]["value"][val]
            mname,mol=self.epmv.getMolName(vname)
            trajname = mname+'.model'
            if adt:
                trajname = mname+'.dlg'
            self.mv.iMolData[mname].append(trajname)
        else :
            mname = molname
            trajname = dataname                         
        self.addItemToPMenu(self.COMB_BOX["dat"],trajname)
        self.mv.iTraj[len(self.COMB_BOX["dat"]["value"])-1]=[trajname,"model"]
        self.current_traj=[trajname,"model"]

    def gromacsTraj(self,file=None,dataname=None,molname=None):
        if molname == None :
            self.mv.openTrajectory(file, log=0)
            trajname=os.path.basename(file)
            #print trajname
            val = self.getLong(self.COMB_BOX["mol"])
            vname = self.COMB_BOX["mol"]["value"][val]
            mname,mol=self.epmv.getMolName(vname) 
            self.mv.iMolData[mname].append(trajname)
            self.mv.playTrajectory(mname, trajname, log=0)
        else :
            mname = molname
            trajname = dataname
        self.addItemToPMenu(self.COMB_BOX["dat"],trajname)
        self.mv.iTraj[len(self.COMB_BOX["dat"]["value"])-1]=[self.mv.Trajectories[trajname],"traj"]
        self.current_traj=[self.mv.Trajectories[trajname],"traj"]
        self.nF=len(self.current_traj[0].coords)
            
    def gridData(self,file=None,dataname=None,molname=None):
        if molname == None :
            self.mv.readAny(file)
#            sys.stderr.write('DObe')
            name = self.mv.grids3D.keys()[-1] #the last read data
            val = self.getLong(self.COMB_BOX["mol"])
            vname = self.COMB_BOX["mol"]["value"][val]
            mname,mol=self.epmv.getMolName(vname) 
            self.mv.cmol = mol
#            sys.stderr.write('before Select and isoContour')            
            self.mv.isoC.select(grid_name=name)		   
            self.mv.isoC(self.mv.grids3D[name],name=mname+"IsoSurface",
                        isovalue=0.)#self.mv.grids3D[name].mean)  
            trajname=name#os.path.basename(filename)
            self.setReal(self.SLIDERS["datS"],0.)
            #print trajname
            if mname == "" and "IsoSurface" not in self.mv.iMolData.keys():
                self.mv.iMolData["IsoSurface"]=[]
                mname = "IsoSurface"
            self.mv.iMolData[mname].append(file)
        else :
            mname = molname
            trajname = dataname
        #self.mv.playTrajectory(mname, trajname, log=0)
        self.addItemToPMenu(self.COMB_BOX["dat"],os.path.basename(trajname))
        self.current_traj = self.mv.iTraj[len(self.COMB_BOX["dat"]["value"])-1]=[self.mv.grids3D[trajname],"grid"]
        self.nF=self.current_traj[0].maxi

    def updateTraj(self,*args):
        i = self.getLong(self.COMB_BOX["dat"])
        if i not in self.mv.iTraj.keys():
            return False
        self.current_traj = self.mv.iTraj[i]
        mini,maxi,default,step = self.epmv.updateTraj(self.current_traj)
        print mini,maxi,default,step
        self.updateSlider(self.SLIDERS["datS"],mini,maxi,default,step)
        return True
        
    def applyState(self,*args):
        #frame=self.GetLong(self.slider)
        mname,mol,sel,selection = self.getDsInfo()
        traj = self.current_traj
        disp = self.mv.molDispl[mname]
        if traj is not None : 
            if traj[1] in ["model" ,"traj"]:
                conf = self.getReal(self.SLIDERS["datS"])
                self.epmv.updateData(traj,int(conf))
                if disp.has_key("surf"):
                    if disp["surf"] : self.updateMSMS(None) #shoudl I redo the coloring?
                if disp.has_key("cms") :
                    if disp["cms"] : self.updateCMS(None)
                self.color(None)
            elif self.current_traj[1] == "grid":
                iso=self.getReal(self.SLIDERS["datS"])#isovalue
                self.mv.isoC(self.current_traj[0],isovalue=iso,name=mname+"IsoSurface")       
            elif hasattr(self.current_traj,'GRID_DATA_FILE'):
                #grid
                iso=self.getReal(self.SLIDERS["datS"])#isoself.GetReal(self.slider)
                self.mv.setIsovalue(self.current_traj[0].name,iso, log = 1)          
        self.updateViewer()
        #return True

    def getDsInfo(self,key=None):
        val = self.getLong(self.COMB_BOX["mol"])
        name = self.COMB_BOX["mol"]["value"][val]
        print name
        mname,mol=self.epmv.getMolName(name) #just in case name is a selection..
        print mname,mol
        selString=self.getString(self.SELEDIT_TEXT)
        sel,selection=self.epmv.getSelectionLevel(mol,selString)
        if key is not None :
            if key != "col" :
                display = self.getBool(self.CHECKBOXS[key])
                self.updateMolDsDict(sel,mname,display,key)
            else :
                display = self.getColor(self.COLFIELD)
            return mname,mol,sel,selection,display
        return mname,mol,sel,selection

    def updateMolDsDict(self,sel,mname,display,key):
        if sel == mname :
            self.mv.molDispl[mname][key]= display
        else :
            self.mv.molDispl[mname][key] = False

#    def deleteMol(self,*args):
#        mname,mol,sel,selection = self.getDsInfo()
#        self.epmv._deleteMolecule(mol)

    def delete_Atom_Selection(self,*args):
        #self.mv.deleteAtomSet...
        mname,mol,sel,selection = self.getDsInfo()
        if sel is mol.name :
#            print sel,mname, mol , "del"
            res = self.drawQuestion("Delete?","Are You sure you want to delete "+mol.name)
            if res : 
                self.epmv._deleteMolecule(mol)
        else :
            res = self.drawQuestion("Delete?","Are You sure you want to delete the atoms of the current selection "+sel)
            if res : 
                self.mv.deleteAtomSet(selection)

    def dsCPK(self,*args):
        print args
        mname,mol,sel,selection,display = self.getDsInfo("cpk")
        scale = self.getReal(self.SLIDERS["cpk"])  
        #should do some dialog here
        #and what about the progress bar
        if not mol.doCPK:
            mol.doCPK = True#drawQuestion("Are You sure you want \nto display the CPK ("+str(len(mol.allAtoms))+" atoms) ","CPK")
        if mol.doCPK:
            self.mv.displayCPK(sel,log=0,negate=(not display),
                        scaleFactor=scale, redraw =0)#redraw?
        #funcColor[ColorPreset2.val-1](molname, [name], log=1)
#        self.updateViewer()
        return True        

    def dsBS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("bs")
        ratio = self.getReal(self.SLIDERS["bs_r"])
        scale = self.getReal(self.SLIDERS["bs_s"])
        bRad = 0.3
        cradius = float(bRad/ratio)*scale
        if not mol.doCPK:
            mol.doCPK = drawQuestion("Are You sure you want \nto display the BallSticks ("+str(len(mol.allAtoms))+" atoms)","Balls and Sticks")
        if mol.doCPK:
            self.mv.displaySticksAndBalls(sel, bRad=0.3*scale, 
                                   cradius =cradius, bScale=0., 
                                   negate=(not bool(display)),
                                   only=False, bquality=0, 
                                   cquality=0) 
        return True  
    
    def dsSS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("ss")
        self.mv.displayExtrudedSS(sel, negate=(not bool(display)), molModes={mname:'From Pross'},
                                               only=False, log=1)
        return True  
            
    def dsCMS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("cms")
        name='CoarseMS_'+mname
        parent=mol.geomContainer.masterGeom.obj 
        iso = self.getReal(self.SLIDERS["cmsI"])
        res = self.getReal(self.SLIDERS["cmsR"])
        print iso,res
        if name not in mol.geomContainer.geoms :
            geom=self.epmv.coarseMolSurface(mol,[32,32,32],
                                        isovalue=iso,resolution=res,
                                        name=name)
            mol.geomContainer.geoms[name]=geom
            obj=self.epmv.helper.createsNmesh(name,geom.getVertices(),None,
                                          geom.getFaces(),smooth=True)
            self.epmv._addObjToGeom(obj,geom)
            self.epmv.helper.addObjectToScene(self.epmv.helper.getCurrentScene(),
                                          obj[0],parent=parent)
            self.mv.colorByAtomType(mname, [name], log=0)
            obj=obj[0]
        else :
            obj = mol.geomContainer.geoms[name].obj
        self.epmv.helper.toggleDisplay(obj,display)
        return True

    def updateCMS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("cms")
        name='CoarseMS_'+mname
        if display and name in mol.geomContainer.geoms.keys():
            parent=mol.geomContainer.masterGeom.obj 
            iso = self.getReal(self.SLIDERS["cmsI"])
            res = self.getReal(self.SLIDERS["cmsR"])            
            #isovalue=7.1#float(cmsopt['iso'].val),
            #resolution=-0.3#float(cmsopt['res'].val)
            g = self.epmv.coarseMolSurface(selection,[32,32,32],
                                      isovalue=iso,
                                      resolution=res,
                                      name=name,
                                      geom = mol.geomContainer.geoms[name])
            self.epmv.helper.updateMesh(g.mesh,vertices=g.getVertices(),
                                          faces=g.getFaces())
        return True
    
    def dsMSMS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("surf")
        name='MSMS-MOL'+mname
        pradius=self.getReal(self.SLIDERS["surf"])
        if name in mol.geomContainer.geoms :
            self.mv.displayMSMS(sel, negate=(not bool(display)), 
                            only=False, surfName=name, nbVert=1)
        else :
            self.mv.computeMSMS(sel, display=(bool(display)), 
                             surfName=name,perMol=1,pRadius=pradius)
        #funcColor[ColorPreset2.val-1](molname, [name], log=1)
        return True
        
    def updateMSMS(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("surf")
        name='MSMS-MOL'+mname
        pradius=self.getReal(self.SLIDERS["surf"])
        if display and name in mol.geomContainer.geoms: 
            self.mv.computeMSMS(sel,#hdensity=msmsopt['hdensity'].val, 
                                     hdset=None, 
#                                     density=msmsopt['density'].val, 
                                     pRadius=pradius, 
                                     perMol=1, display=True, 
                                     surfName=name)
        return True

    def dsLoft(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("loft")
        name="loft"+mol.name
        loft = self.epmv.helper.getObject(name)
        if loft is None :
            if sel == mname :
                selection = mol.allAtoms.get("CA")
            selection.sort()
            loft = self.epmv._makeRibbon("loft"+mol.name,selection.coords,
                                     parent=mol.geomContainer.masterGeom.obj)
        self.epmv.helper.toggleDisplay(loft,display)
        return True
    
    def dsSpline(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("spline")
        for c in mol.chains :
            name=mol.name+"_"+c.name+"spline"#'spline'+mol.name #
            obSpline=self.epmv.helper.getObject(name)
            if obSpline is None:
                if sel == mname :
                    selection = c.residues.atoms.get("CA")
                selection.sort()
                parent = mol.geomContainer.masterGeom.chains_obj[c.name]
                obSpline,spline=self.epmv.helper.spline(name,selection.coords,
                                                scene=self.epmv.helper.getCurrentScene(),
                                                parent=parent)
            self.epmv.helper.toggleDisplay(obSpline,display)
        return True
        
    def dsMeta(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("meta")
        #make the metaballs
        name='metaballs'+mol.name
        metaballs=self.epmv.helper.getObject(name)
        if metaballs is None :
#            atoms = selection.allAtoms #or a subselection of surface atoms according sas
            metaballsModifyer,metaballs = self.epmv._metaballs(name,
                                                selection.coords,
                                                selection.radius,
                                                scn=self.epmv.helper.getCurrentScene(),
                                                root=mol.geomContainer.masterGeom.obj)
        else :
            self.epmv.helper.toggleDisplay(metaballs,display)
        return True
        
    def dsBones(self,*args):
        mname,mol,sel,selection,display = self.getDsInfo("arm")
        name=mname+"_Armature"
        armObj = self.epmv.helper.getObject(name)
        if armObj is None :
            if sel == mname :
                selection = mol.allAtoms.get("CA")
            selection.sort()        
            object,bones=self.epmv._armature(name,selection,
                                       scn=self.epmv.helper.getCurrentScene(),
                                       root=mol.geomContainer.masterGeom.obj)
            mol.geomContainer.geoms["armature"]=[object,bones]
        else :
            self.epmv.helper.toggleDisplay(armObj,display)
        return True
        
    def color(self,*args):
#        print self.funcColor
        mname,mol,sel,selection,color = self.getDsInfo("col")
        lGeom=self.getGeomActive(mname)
        funcId = self.getLong(self.COMB_BOX["col"])
#        print "colorF ", funcId,self.funcColor[funcId], lGeom
        if funcId == 6 : 
            #custom color
            self.mv.molDispl[mname]["col"]=color
            self.funcColor[6](selection,[color], lGeom, log=1)
        elif funcId == 7 or funcId == 8 or funcId == 9  :
            #color by properties , ie NtoC, Bfactor, SAS
            self.mv.colorByProperty.level='Atom'
            if funcId == 7 :
                maxi = len(selection)
                mini = 1.0
                property = 'number'
            elif funcId == 8 :
                maxi = max(selection.temperatureFactor)
                mini = min(selection.temperatureFactor)
                property = 'temperatureFactor'
            elif funcId == 9 : 
                if not hasattr(selection,"sas_area"):
                    try :
                        self.mv.computeSESAndSASArea(mol)
                    except :
                        self.drawError("Problem with mslib")
                maxi = max(selection.sas_area)
                mini = min(selection.sas_area)
                property = 'sas_area'
            self.funcColor[7](selection, lGeom, property,mini=float(mini),
                                        maxi=float(maxi), propertyLevel='Atom', 
                                        colormap='rgb256')
            self.mv.molDispl[mname]["col"] = funcId
        else : 
            self.funcColor[funcId](selection, lGeom)
            self.mv.molDispl[mname]["col"] = funcId

    def drawPreset(self,*args):
        #To finish and define/...
        mname,mol,sel,selection = self.getDsInfo()
#        self.presettype=['available presets:','  Lines','  Liccorice','  SpaceFilling',
#                         '  Ball+Sticks','  RibbonProtein+StickLigand',
#                         '  RibbonProtein+CPKligand','  xray','  Custom',
#                         '  Save Custom As...']
        #load,edit save representation preset
        preset=self.presettype[self.getLong(self.COMB_BOX["preset"])]
        print preset
        if preset.strip() == 'Liccorice':
            #displayBS as licorice which is simply ratio == 1.0
                #set the ratio and do the command
            self.setReal(self.SLIDERS["bs_r"],1.0)
            self.setBool(self.CHECKBOXS["bs"] ,True)
            self.dsBS()
        elif preset.strip() == 'RibbonProtein+StickLigand':
            #need 1 or 2 molecules...like whats prot and whats ligand
            #lets ask for it ? with some proposition
            pass
        elif preset.strip() == 'xray':
            #??
            pass
        elif preset.strip() == 'Lines':
            self.mv.displayLines(selection)
        
    def setKeywordSel(self,*args):
        key=self.keyword[self.getLong(self.COMB_BOX["keyword"])]
        if key == 'keywords' : key = ""
        self.setString(self.SELEDIT_TEXT,key.replace(" ",""))

    def set_ePMVScript(self,*args):
        from ePMV import demo
        dir = demo.__path__[0]
        ids = self.getLong(self.COMB_BOX['scriptO'])
        filename = None
        if ids == 0 : #Open..ask for broser
            self.fileDialog(label="Open python file",callback=self.set_ePMVScript_cb)
        else :
            filename = dir+'/'+self.scriptliste[ids]+'.py'
            self.set_ePMVScript_cb(filename)

    def set_ePMVScript_cb(self,filename):
        if filename :
            try:
                f = open(filename,'r')
                script = f.read()
                f.close()
            except:
                script = "file :\n"+filename + " didnt exist !\n"
            self.SetStringArea(self.SCRIPT_TEXT,script)
 
    def execPmvComds(self,*args):
        #first select the text
        #cmds=pmvcmds.val
        text = self.getStringArea(self.SCRIPT_TEXT)# getSelectTxt()
        if text is not None:
            cmds=text
#            for l in text:
#                cmds+=l+'\n'
#            print len(cmds),cmds
            exec(cmds,{'self':self.mv,'epmv':self.epmv})  
#            self.updateViewer()
            return True

    def drawPreferences(self,*args):
        #drawSubDialog
        self.drawSubDialog(self.options,2555554,callback = self.options.SetPreferences) #in c4d asynchr but blender syncrho
#        self.options.Open(c4d.DLG_TYPE_ASYNC, pluginid=2555554, defaultw=250, defaulth=200)

    def drawAbout(self,*args):
        self.drawMessage(title='About ePMV',message=self.__about__)
        
    def launchBrowser(self,*args):
        import webbrowser
        webbrowser.open(self.__url__[0])
        
    def citationInformation(self,*args):
        import webbrowser
        webbrowser.open(self.__url__[2])
 
    def addExtensionGUI(self,*args):
        question="Enter the extension name follow by the directory,\nie 'modeller:/Library/modeller/modlib'"
        self.drawInputQuestion(question=question,callback=self.epmv.inst.addExtension)

    def drawModellerGUI(self,*args):
        #drawSubDialog
        self.drawSubDialog(self.pd,2555556,callback = self.pd.doIt) #in c4d asynchr but blender syncrho
#        self.options.Open(c4d.DLG_TYPE_ASYNC, pluginid=2555554, defaultw=250, defaulth=200)

    def modellerOptimize(self,*args):
        import modeller
        mname,mol,sel,selection = self.getDsInfo()     
        mdl = mol.mdl
        mdl = mol.mdl
        print mname
        # Select all atoms:
        atmsel = modeller.selection(mdl)
        
        # Generate the restraints:
        mdl.restraints.make(atmsel, restraint_type='stereo', spline_on_site=False)
        #mdl.restraints.write(file=mpath+mname+'.rsr')
        mpdf = atmsel.energy()
        print "before optmimise"
        # Create optimizer objects and set defaults for all further optimizations
        cg = modeller.optimizers.conjugate_gradients(output='REPORT')
        mol.pmvaction.last = 10000
        print "optimise"
        maxit = self.pd.getLong(self.pd.NUMBERS['miniIterMax'])
        mol.pmvaction.store = self.pd.getBool(self.pd.CHECKBOXS['store'])
        mol.pmvaction.redraw = True
        cg.optimize(atmsel, max_iterations=maxit, actions=mol.pmvaction)#actions.trace(5, trcfil))
        del cg
        mol.pmvaction.redraw = False
        return True
        
    def modellerMD(self,*args):
        import modeller
        mname,mol,sel,selection = self.getDsInfo()     
        mdl = mol.mdl
        print mname
        # Select all atoms:
        atmsel = modeller.selection(mdl)
        
        # Generate the restraints:
        mdl.restraints.make(atmsel, restraint_type='stereo', spline_on_site=False)
        #mdl.restraints.write(file=mpath+mname+'.rsr')
        mpdf = atmsel.energy()
        print "before optmimise"
        md = modeller.optimizers.molecular_dynamics(output='REPORT')
        mol.pmvaction.last = 10000
        mol.pmvaction.store = True
        print "optimise"
        maxit = self.pd.getLong(self.pd.NUMBERS['mdIterMax'])
        temp = self.pd.getLong(self.pd.NUMBERS['mdTemp'])
        mol.pmvaction.store = self.pd.getBool(self.pd.CHECKBOXS['store'])
        print maxit,temp,mol.pmvaction.store
        mol.pmvaction.redraw = True
        md.optimize(atmsel, temperature=float(temp), max_iterations=int(maxit),actions=mol.pmvaction)
        del md
        mol.pmvaction.redraw = False
        return True

