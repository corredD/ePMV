# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 22:44:30 2011

@author: Ludovic Autin
"""
import upy
try :
    from upy import uiadaptor
    if uiadaptor is None :
        uiadaptor = upy.getUIClass()
except :
    uiadaptor = None

from ePMV.extension._prody._prody import _prodymodel

class prodyGui(uiadaptor):
    keywords = {
        "mode" :0,
        "rmsd" : 0.8,
        "nbconf" : 10,
        "conf" : "protein",
        "cutoff" : 15.0,
        "gamma" : 1.0,
        "gammaStructure" : False,
        "sample" : "sample",#or traverse
    }
    
    def setup(self,sub=True,epmv=None,id=2000):
        self.subdialog = sub
        self.title = "Prody"
        self.epmv = epmv
        self.mv = epmv.mv
        self.w = 350
        self.h = 300
        self.mode = 0
        self.firsttime = True
        if self.subdialog:
            self.block = True
        witdh=350
        if id is not None :
            id=id
        else:
            id = self.bid
        #define the button here
        self.LABELS={}        
        self.BTN={}
        self.COMBO={}
        self.CHKBOX={}
        self.INSTR={}
        self.INPUT={}    
        self.SEP={}
        if self.epmv is not None : #work on the current_mol
#            for k in _prody.keywords:
            self.LABELS["header"] = self._addElemt(label="Prody plugin for ePMV",width=120)
            self.LABELS["current"] = self._addElemt(label="applied on the current epmv mol",width=120)
            
            self.LABELS["conf"] = self._addElemt(label="conf type",width=120)            
            self.INPUT["conf"] = self._addElemt(name="conf type",width=100,height=10,
                                              action=None,type="inputStr",icon=None,
                                              value="protein",
                                              variable=self.addVariable("str","protein"))            
            self.LABELS["rmsd"] = self._addElemt(label="rmsd",width=120)            
            self.INPUT["rmsd"] = self._addElemt(name="rmsd",width=20,height=10,
                                              action=None,type="sliders",icon=None,
                                              value=0.8,mini=0.,maxi=10.,step=0.1,
                                              variable=self.addVariable("float",1.0))
            self.LABELS["cutoff"] = self._addElemt(label="cutoff",width=120) 
            self.INPUT["cutoff"] = self._addElemt(name="cutoff",width=20,height=10,
                                              action=None,type="sliders",icon=None,
                                              value=15.0,mini=4.,maxi=30.,step=1.0,
                                              variable=self.addVariable("float",1.0))
            self.LABELS["gamma"] = self._addElemt(label="gamma",width=120) 
            self.INPUT["gamma"] = self._addElemt(name="gamma",width=20,height=10,
                                              action=None,type="sliders",icon=None,
                                              value=1.0,mini=0.,maxi=10.,step=0.1,
                                              variable=self.addVariable("float",1.0))
            
            self.LABELS["gammaStructure"] = self._addElemt(label="gammaStructure",width=120) 
            self.INPUT["gammaStructure"] =self._addElemt(name="gammaStructure",width=80,height=10,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
                                              
            self.LABELS["nbconf"] = self._addElemt(label="nbconf",width=120)                                  
            self.INPUT["nbconf"] = self._addElemt(name="nbconf",width=20,height=10,
                                              action=None,type="inputInt",icon=None,
                                              value=1,mini=1,maxi=200,step=1,
                                              variable=self.addVariable("int",1)) 
            self.LABELS["mode"] = self._addElemt(label="mode",width=120) 
            self.INPUT["mode"] = self._addElemt(name="mode",width=100,height=10,
                                            type="sliders",label="mode",
                                              variable=self.addVariable("int",0),
                                             mini=0,maxi=10,step=1)                                             
            self.sample=['sample','traverse']
            self._sample=self.addVariable("int",1)
            self.LABELS["sample"] = self._addElemt(label="sample method",width=120) 
            self.INPUT["sample"] = self._addElemt(name="Sample",value=self.sample,
                                    width=60,height=10,
                                    variable=self._sample,
                                    type="pullMenu")
                                    
            self.SEP["run"]=self._addElemt(name="run",type="line",value="H")
            self.SEP["mode"]=self._addElemt(name="mode",type="line",value="H")
            self.SEP["close"]=self._addElemt(name="close",type="line",value="H")
            
            self.BTN["mode"] = self._addElemt(name="apply mode",width=50,height=10,
                              label = 'apply mode',
                         action=self.togglemode,type="button")     
            self.BTN["run"] = self._addElemt(name="compute",width=50,height=10,
                              label = 'comute Normal Mode using current paramters',
                         action=self.runPrody,type="button")
            self.BTN["ok"] = self._addElemt(name="Close",width=50,height=10,
                         action=self.cancel,type="button")
        self.setupLayout()
#        self.restorePreferences()
        return True

    def setupLayout(self):
        self._layout = []
        self._layout.append([self.LABELS["header"],])
        self._layout.append([self.LABELS["current"],])
        self._layout.append([self.SEP["run"],])        
        l1 =  ["gamma","gammaStructure","cutoff","conf"]
        for  l in l1 :
            self._layout.append([self.LABELS[l],self.INPUT[l]])        
        self._layout.append([self.BTN["run"],])
        self._layout.append([self.SEP["mode"],]) 
        l1 =  ["mode","rmsd","nbconf","sample"]
        for  l in l1 :
            self._layout.append([self.LABELS[l],self.INPUT[l]])       
        self._layout.append([self.BTN["mode"],])
        self._layout.append([self.SEP["close"],])    
        self._layout.append([self.BTN["ok"],])
        
    def setOptions(self,*args):
        if self.epmv is not None :
            mname,mol,sel,selection = self.epmv.gui.getDsInfo()
            dicD= self.mv.molDispl[mname]
            #check if the molecule already have a prody strueattached
            if not hasattr(mol,"prodymodel") or mol.prodymodel is None:
                return
            kw={}
            for k in self.keywords:
                kw[k] = self.getVal(self.INPUT[k])
                print (k,kw[k])
            mol.prodymodel.Set(**kw)

    def CreateLayout(self):
        self._createLayout()
        return True
    def Command(self,*args):
#        print args
        self._command(args)
        return True

    def cancel(self,*args):
        self.close()                 

    def runPrody(self,*args):
        if self.epmv is not None :
            mname,mol,sel,selection = self.epmv.gui.getDsInfo()
            dicD= self.mv.molDispl[mname]
            #check if the molecule already have a prody strueattached
            if not hasattr(mol,"prodymodel") or mol.prodymodel is None:
                #what about centered mol? what if I dump from pmv ? and read it
                mol.prodymodel = _prodymodel(mol.parser.filename)
                mol.prodymodel.setPMVmodel(mol)
            self.setOptions()
            mol.prodymodel.computeNormalMode()
            #updaethe pull down / slidermenu for choosing the current mode to be apply to the objec
            self.updateSlider(self.INPUT["mode"],0,mol.prodymodel.nbMode,0,1)

    def togglemode (self,*args):     
        if self.epmv is not None :
            mname,mol,sel,selection = self.epmv.gui.getDsInfo()
            if not hasattr(mol,"prodymodel") or mol.prodymodel is None:
                return
            self.setOptions()
            self.mode+=1
            if self.mode > mol.prodymodel.nbMode:
                self.mode = 0
            mol.prodymodel.applyMode(self.mode) 
            if self.firsttime :
                self.epmv.gui.loadDATA(None,model=True)
                self.firsttime = False
            else :
                #need to update
                self.epmv.gui.updateTraj(None)

                            