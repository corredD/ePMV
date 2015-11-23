
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/pmv_dev/buildDNAGui.py is part of ePMV.

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
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 23:06:53 2012

@author: Ludovic Autin
"""
import upy
from upy import uiadaptor

class BuildDNAGui(uiadaptor):
    #savedialog dont work
    def setup(self,epmv,id=None):
        self.subdialog = True
        self.block = True
        self.epmv = epmv
        self.title = "Build DNA from sequence w3dna"#+self.mol.name
        self.SetTitle(self.title)
        witdh=350
        self.h=130
        self.w=300
        if id is not None :
            id=id
        else:
            id = self.bid
        self.id = id
        #define the widget here too       
        
        self.BTN={}
        self._name = self.addVariable("str","s0.pdb")
        self.NAME = self._addElemt(name="name",action=None,width=100,
                          value="",type="inputStr",variable=self._name) 

        self._sequence = self.addVariable("str","")
        self.SEQ = self._addElemt(name="seq",action=None,width=100,
                          value="",type="inputStr",variable=self._sequence) 
                                  
        self.sObject = ["M1>A-DNA  (generic)","M4>B-DNA  (generic)","M7>C-DNA  (generic)","M54>A-DNA  (generic alternate)"]#pointsClouds ?
        self.COMB_BOX = self._addElemt(name="Type",
                                    value=self.sObject,
                                    width=100,height=10,action=None,
                                    variable=self.addVariable("int",0),
                                    type="pullMenu",)
        self.BTN["ok"] = self._addElemt(name="Build",width=40,height=10,
                         action=self.build,type="button")
        self.BTN["cancel"] = self._addElemt(name="Cancel",width=40,height=10,
                         action=self.close,type="button")
        self.LABEL0 = self._addElemt(label="Enter a name (ie test.pdb) :",width=100)
        self.LABEL1 = self._addElemt(label="Enter a Sequence :",width=100)
        self.LABEL2 = self._addElemt(label="Choose a type :",width=100)
        self.setupLayout()
        
    def setupLayout(self):
        #form layout for each SS types ?
        self._layout = []
        self._layout.append([self.LABEL0,self.NAME])
        self._layout.append([self.LABEL1,self.SEQ])
        self._layout.append([self.LABEL2,self.COMB_BOX])
        self._layout.append([self.BTN["ok"],self.BTN["cancel"]])

        
    def build(self,*args):
        #get the filename, should we use a file browser?
        mode = self.sObject[self.getLong(self.COMB_BOX)].split(">")[0]
        name = self.getVal(self.NAME)#or self._name
        seq = self.getVal(self.SEQ)#or self._sequence
        #do the transform
        name, pathTo = self.epmv.mv.buildDNA(name,seq=seq,fiberform=mode,load=False)
        if name is None : return        
        if self.epmv.gui is not None :
            self.epmv.gui.loadPDB(pathTo+name)
        else :
            self.epmv.mv.readMolecule(pathTo+name)
        self.close()

    def CreateLayout(self):
        self._createLayout()
        #self.restorePreferences()
        return True

    def Command(self,*args):
#        print args
        self._command(args)
        return True
        
        
        
#completelistof option for the type of dna fiber        
#       <option value="note">Choose a DNA fiber</option>
#        <option value="M1" selected="selected">A-DNA  (generic)</option>
#        <option value="M4">B-DNA  (generic)</option>
#        <option value="M7">C-DNA  (generic)</option>
#        <option value="M54">A-DNA  (generic alternate)</option>
#        <option value="M55">B-DNA  (generic alternate)</option>
#        <option value="M46">B-DNA  (generic alternate) (BI-type nucleotides)</option>
#        <option value="M47">C-DNA  (generic alternate) (BII-type nucleotides)</option>
#        <option value="M53">C-DNA  (generic alternate) (left-handed)</option>
#        <option value="bar">~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~</option>
#        <option value="M2">A-DNA  poly d(ABr5U) : poly d(ABr5U)</option>
#        <option value="M3">A-DNA  poly d(A1T2C3G4G5A6A7T8G9G10T11) : poly d(A...</option>
#        <option value="M5">B-DNA  poly d(CG) : poly d(CG)</option>
#        <option value="M6">B-DNA  poly d(C1C2C3C4C5) : poly d(G6G7G8G9G10)</option>
#        <option value="M44">B-DNA  poly d(A) : poly d(T) (Ca salt)</option>
#        <option value="M45">B-DNA  poly d(A) : poly d(T) (Na salt)</option>
#        <option value="M43">B-DNA  beta poly d(A) : poly d(U)</option>
#        <option value="M41">B'-DNA poly d(AATT) : poly d(AATT)</option>
#        <option value="M18">B'-DNA alpha poly d(A) : poly d(T) (H-DNA)</option>
#        <option value="M38">B'-DNA beta1  poly d(A) : poly d(T)</option>
#        <option value="M40">B'-DNA beta1  poly d(AI) : poly d(CT)</option>
#        <option value="M19">B'-DNA beta2 poly d(A) : poly d(T) (H-DNA  beta)</option>
#        <option value="M37">B'-DNA beta2 poly d(A) : poly d(U)</option>
#        <option value="M39">B'-DNA beta2  poly d(AI) : poly d(CT)</option>
#        <option value="M51">B*-DNA poly d(A) : poly d(T)</option>
#        <option value="M8">C-DNA  poly d(GGT) : poly d(ACC)</option>
#        <option value="M9">C-DNA  poly d(G1G2T3) : poly d(A4C5C6)</option>
#        <option value="M10">C-DNA  poly d(AG) : poly d(CT)</option>
#        <option value="M11">C-DNA  poly d(A1G2) : poly d(C3T4)</option>
#        <option value="M12">D-DNA  poly d(AAT) : poly d(ATT)</option>
#        <option value="M13">D-DNA  poly d(CI) : poly d(CI)</option>
#        <option value="M14">D-DNA  poly d(A1T2A3T4A5T6) : poly d(A1T2A3T4A5T6)</option>
#        <option value="M48">D_A-DNA  poly d(AT) : poly d(AT) (right-handed)</option>
#        <option value="M52">D_B-DNA  poly d(AT) : poly d(AT)</option>
#        <option value="M17">L-DNA  poly d(GC) : poly d(GC)</option>
#        <option value="M49">S-DNA  poly d(CG) : poly d(CG) (C_BG_A, right-hand...</option>
#        <option value="M50">S-DNA  poly d(GC) : poly d(GC) (C_AG_B, right-hand...</option>
#        <option value="M15">Z-DNA  poly d(GC) : poly d(GC)</option>
#        <option value="M16">Z-DNA  poly d(As4T) : poly d(As4T)</option>
#        <option value="M30">DNA poly d(C) : poly d(I) : poly d(C)</option>
#        <option value="M31">DNA poly d(T) : poly d(A) : poly d(T)</option>
#        <option value="M22">DNA-RNA hybrid poly (A) : poly d(T)</option>
#        <option value="M23">DNA-RNA hybrid poly d(G) : poly (C)</option>
#        <option value="M24">DNA-RNA hybrid poly d(I) : poly (C)</option>
#        <option value="M25">DNA-RNA hybrid poly d(A) : poly (U)</option>
#        <option value="M20">A-RNA  poly (A) : poly (U)</option>
#        <option value="M27">A-RNA 11-fold poly (X) : poly (X)</option>
#        <option value="M28">A-RNA poly (s2U) : poly (s2U) (symmetric)</option>
#        <option value="M29">A-RNA poly (s2U) : poly (s2U) (asymmetric)</option>
#        <option value="M21">A'-RNA poly (I) : poly (C)</option>
#        <option value="M26">RNA 10-fold poly (X) : poly (X)</option>
#        <option value="M32">RNA poly (U) : poly (A) : poly(U) (11-fold)</option>
#        <option value="M33">RNA poly (U) : poly (A) : poly(U) (12-fold)</option>
#        <option value="M34">RNA poly (I) : poly (A) : poly(I)</option>
#        <option value="M35">RNA poly (I) : poly (I) : poly(I) : poly(I)</option>
#        <option value="M36">RNA poly (C) or poly (mC) or poly (eC)</option>
#        <option value="M42">RNA poly (U) : poly d(A) : poly(U)</option>
# 