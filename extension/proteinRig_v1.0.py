#proteinRig_v1.0 initial release 8/4/2014
#by Nathaniel Smith, Diana Zajac and Dan Gurnon


import c4d
from c4d import gui


def AA_hierarchy(op):                        #Creates Amino Acid Hierarchies for long-chain AAs
    sc = op.GetDown().GetNext()
    null = op.GetDown().GetNext().GetDown()
    nullList = sc.GetChildren()
    fracList = []
    for null in nullList:
            
        #Arginine    
        if null.GetName()[0] == "R":
            beta = null.GetDown()
            gammaC = beta.GetNext()
            deltaC = gammaC.GetNext()
            epsilonN = deltaC.GetNext()
            zetaC = epsilonN.GetNext()
            hyd1N = zetaC.GetNext()
            hyd2N = hyd1N.GetNext()
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(beta)
            mg = beta.GetMg()
            frac.SetMg(mg)
            mg = gammaC.GetMg()
            gammaC.InsertUnder(frac)
            gammaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(gammaC)
            mg = gammaC.GetMg()
            frac.SetMg(mg)
            mg = deltaC.GetMg()
            deltaC.InsertUnder(frac)
            deltaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(deltaC)
            mg = deltaC.GetMg()
            frac.SetMg(mg)
            mg = epsilonN.GetMg()
            epsilonN.InsertUnder(frac)
            epsilonN.SetMg(mg)
            mg = zetaC.GetMg()
            zetaC.InsertUnder(epsilonN)
            zetaC.SetMg(mg)
            mg = hyd1N.GetMg()
            hyd1N.InsertUnder(epsilonN)
            hyd1N.SetMg(mg)
            mg = hyd2N.GetMg()
            hyd2N.InsertUnder(epsilonN)
            hyd2N.SetMg(mg)
            fracList.append(frac)
            
        #Glutamic Acid    
        if null.GetName()[0] == "E":
            beta = null.GetDown()
            gammaC = beta.GetNext()
            deltaC = gammaC.GetNext()
            epsilon1O = deltaC.GetNext()
            epsilon2O = epsilon1O.GetNext()
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(beta)
            mg = beta.GetMg()
            frac.SetMg(mg)
            mg = gammaC.GetMg()
            gammaC.InsertUnder(frac)
            gammaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(gammaC)
            mg = gammaC.GetMg()
            frac.SetMg(mg)
            mg = deltaC.GetMg()
            deltaC.InsertUnder(frac)
            deltaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(deltaC)
            mg = deltaC.GetMg()
            frac.SetMg(mg)
            mg = epsilon1O.GetMg()
            epsilon1O.InsertUnder(frac)
            epsilon1O.SetMg(mg)
            mg = epsilon2O.GetMg()
            epsilon2O.InsertUnder(frac)
            epsilon2O.SetMg(mg)
            fracList.append(frac)
            
        #Lysine   
        if null.GetName()[0] == "K":
            beta = null.GetDown()
            gammaC = beta.GetNext()
            deltaC = gammaC.GetNext()
            epsilonC = deltaC.GetNext()
            zetaN = epsilonC.GetNext()
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(beta)
            mg = beta.GetMg()
            frac.SetMg(mg)
            mg = gammaC.GetMg()
            gammaC.InsertUnder(frac)
            gammaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(gammaC)
            mg = gammaC.GetMg()
            frac.SetMg(mg)
            mg = deltaC.GetMg()
            deltaC.InsertUnder(frac)
            deltaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(deltaC)
            mg = deltaC.GetMg()
            frac.SetMg(mg)
            mg = epsilonC.GetMg()
            epsilonC.InsertUnder(frac)
            epsilonC.SetMg(mg)
            mg = zetaN.GetMg()
            zetaN.InsertUnder(frac)
            zetaN.SetMg(mg)
            fracList.append(frac)
            
        #Methionine   
        if null.GetName()[0] == "M":
            beta = null.GetDown()
            gammaC = beta.GetNext()
            deltaS = gammaC.GetNext()
            epsilonC = deltaS.GetNext()
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(beta)
            mg = beta.GetMg()
            frac.SetMg(mg)
            mg = gammaC.GetMg()
            gammaC.InsertUnder(frac)
            gammaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(gammaC)
            mg = gammaC.GetMg()
            frac.SetMg(mg)
            mg = deltaS.GetMg()
            deltaS.InsertUnder(gammaC)
            deltaS.SetMg(mg)
            mg = epsilonC.GetMg()
            epsilonC.InsertUnder(gammaC)
            epsilonC.SetMg(mg)
            fracList.append(frac)
    
        #Glutamine   
        if null.GetName()[0] == "Q":
            beta = null.GetDown()
            gammaC = beta.GetNext()
            deltaC = gammaC.GetNext()
            epsilon1O = deltaC.GetNext()
            epsilon2N = epsilon1O.GetNext()
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(beta)
            mg = beta.GetMg()
            frac.SetMg(mg)
            mg = gammaC.GetMg()
            gammaC.InsertUnder(frac)
            gammaC.SetMg(mg)
            fracList.append(frac)
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(gammaC)
            mg = gammaC.GetMg()
            frac.SetMg(mg)
            mg = deltaC.GetMg()
            deltaC.InsertUnder(frac)
            deltaC.SetMg(mg)
            fracList.append(frac) 
            
            frac = c4d.BaseObject(1018791)
            frac.InsertUnder(deltaC)
            mg = deltaC.GetMg()
            frac.SetMg(mg)
            mg = epsilon1O.GetMg()
            epsilon1O.InsertUnder(frac)
            epsilon1O.SetMg(mg)
            mg = epsilon2N.GetMg()
            epsilon2N.InsertUnder(frac)
            epsilon2N.SetMg(mg)
            fracList.append(frac)    

        c4d.EventAdd()    

    return fracList

def OnlyProtein(obj,allList=[]):           #Populates a list of all children of op selection        
    c4d.CallCommand(100004768)
    allObjs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    allList = []
    for obj in allObjs:
        allList.append(obj)
        
    return allList

def FindAtoms(obj,atom_list=[]):            #Populates a list of all CPK atoms
    allList = OnlyProtein(op)
    for obj in allList:
        if obj.GetName()[:2].find("S.") >= 0:
            atom_list.append(obj)
            
    return atom_list

def FindCB(obj,cb_list=[]):                 #Locates all Beta Carbon atoms
    allList = OnlyProtein(op)
    for obj in allList:
        if obj.GetName().find(".CB") >= 0:
            cb_list.append(obj)
    
    return cb_list

def FindP (op, pro_list=[]):                #Locates Proline atoms
    atom_list = FindAtoms(op)
    pro_list = []
    for op in atom_list:
        if op.GetName().split(".")[3][0] == "P":
            pro_list.append(op)

    return pro_list
    
def GroupAtoms(op,namefilter,group_op):     #Groups atoms by amino acid, leaves out proline
    atom_list = FindAtoms(op)
    opList = []
    for op in atom_list:
        cb_name = op.GetName() 
        if cb_name.split(".")[3] == namefilter:
            opList.append(op)
        if op.GetDown(): GroupAtoms(op.GetDown(),namefilter,group_op)
        op = op.GetNext()

    for op in opList:
        mg = op.GetMg()
        if op.GetName().split(".")[3][0] == "P":
            None
        else:
            op.InsertUnder(group_op)
        op.SetMg(mg)
    
def FindBB(obj,bb_list=[]):                  #Populates a list of backbone atoms
    allList = OnlyProtein(op)
    for obj in allList:
        if obj.GetName().find(".CA.") >= 0:
            bb_list.append(obj)
        if obj.GetName().find(".C.") >= 0:
            bb_list.append(obj)
        if obj.GetName().find(".O.") >= 0:
            bb_list.append(obj)
        if obj.GetName().find(".N.") >= 0:
            bb_list.append(obj)  
        if obj.GetName().find(".CH3.") >= 0:
            bb_list.append(obj)  
        if obj.GetName().find(".OXT.") >= 0:
            bb_list.append(obj)  
    
    return bb_list

def RotEffect(RotEff=[]):           #Returns current effectors in own lists        
    c4d.CallCommand(100004766)
    allObjs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    RotEff = []
    for obj in allObjs:
        if obj.GetName() == "Sidechain Rotation":
            RotEff.append(obj)
        
    return RotEff

def PosEffect(PosEff=[]):           #Returns current effectors in own lists        
    c4d.CallCommand(100004766)
    allObjs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    PosEff = []
    for obj in allObjs:
        if obj.GetName() == "Atom Vibration":
            PosEff.append(obj)
        
    return PosEff

def main1(op):
    
    cb_list = FindCB(op)                    #Imports beta carbon atom list and backbone atom list
    bb_list = FindBB(op)
    
    SCfrac = c4d.BaseObject(1018791)        #Creates Sidechain and Backbone Fractures for randomized animation
    SCeffect_list = SCfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    SCfrac.InsertUnder(op)
    SCfrac.SetName("Sidechains")
    
    BBfrac = c4d.BaseObject(1018791)
    BBeffect_list = BBfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    BBfrac.InsertUnder(op)
    BBfrac.SetName("Backbone")
    
    for cb_op in cb_list:                   #Makes nulls for every amino acid sidechain
        cb_null = c4d.BaseObject(c4d.Onull)
        cb_name = cb_op.GetName()
        cb_null.SetName(cb_name.split(".")[3])
        cb_null.InsertUnder(SCfrac)
        cb_null.SetMg(cb_op.GetMg())
        GroupAtoms(doc.GetActiveObject(),cb_name.split(".")[3],cb_null)
        
    for bb_op in bb_list:                   #Inserts backbone atoms under the backbone fracture
        mg = bb_op.GetMg()
        bb_op.InsertUnder(BBfrac)
        bb_op.SetMg(mg)
        
    pro_list = FindP(op)                    #Adds proline atoms back into the sidechain fracture
    for pro in pro_list:
        pro.InsertUnder(SCfrac)
        
    
    fracList = AA_hierarchy(op)             #Runs the hierarchy script
    
                                           #Creates effectors for random rotation and position
    RotEff = RotEffect()
    PosEff = PosEffect()
    
    
    if RotEff == []:    
        obj = c4d.BaseObject(1018643)    
        obj.SetName("Sidechain Rotation")
        doc.InsertObject(obj)
        obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        obj[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = 0
        obj[c4d.ID_MG_BASEEFFECTOR_ROTATE_ACTIVE] = 1
        obj[c4d.ID_MG_BASEEFFECTOR_ROTATION] = c4d.Vector(c4d.utils.Rad(50),c4d.utils.Rad(50),c4d.utils.Rad(50))
        obj[c4d.MGRANDOMEFFECTOR_MODE] = 2
        obj[c4d.MGRANDOMEFFECTOR_INDEXED] = 1
        obj[c4d.MGRANDOMEFFECTOR_SPEED] = 0.8
        SCeffect_list.InsertObject(obj,1)
        SCfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = SCeffect_list  
        for AAfrac in fracList:
            AAeffect_list = AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
            AAeffect_list.InsertObject(obj,1)
            AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = AAeffect_list
            
    else:
        for obj in RotEff:
            if obj.GetName() == "Sidechain Rotation":
                SCeffect_list.InsertObject(obj,1)
                SCfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = SCeffect_list  
                for AAfrac in fracList:
                    AAeffect_list = AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
                    AAeffect_list.InsertObject(obj,1)
                    AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = AAeffect_list
                    
    if PosEff == []:    
        obj1 = c4d.BaseObject(1018643)
        obj1.SetName("Atom Vibration")
        doc.InsertObject(obj1)
        obj1[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
        obj1[c4d.ID_MG_BASEEFFECTOR_TRANSFORMMODE] = 1
        obj1[c4d.ID_MG_BASEEFFECTOR_POSITION] = c4d.Vector(0.2,0.2,0.2)
        obj1[c4d.MGRANDOMEFFECTOR_MODE] = 2
        obj1[c4d.MGRANDOMEFFECTOR_INDEXED] = 1
        obj1[c4d.MGRANDOMEFFECTOR_SPEED] = 3
        SCeffect_list.InsertObject(obj1,1)
        SCfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = SCeffect_list 
        BBeffect_list.InsertObject(obj1,1) 
        BBfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = BBeffect_list
        for AAfrac in fracList:
            AAeffect_list = AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
            AAeffect_list.InsertObject(obj1,1)
            AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = AAeffect_list
            
    else:
        for obj1 in PosEff:
            if obj1.GetName() == "Atom Vibration":
                SCeffect_list.InsertObject(obj1,1)
                SCfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = SCeffect_list 
                BBeffect_list.InsertObject(obj1,1) 
                BBfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = BBeffect_list
                for AAfrac in fracList:
                    AAeffect_list = AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
                    AAeffect_list.InsertObject(obj1,1)
                    AAfrac[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST,] = AAeffect_list
    
    c4d.EventAdd()
    c4d.CallCommand(100004767)
    
    print "Your protein is now animated. Click play."
    
def main():                                #Gives feedback to user based on user interaction
    op = doc.GetActiveObject()
    if doc.GetActiveObject() == None:
        gui.MessageDialog("Please select a molecule")
    else:
        atom_list = FindAtoms(op)
        if atom_list == []:
            gui.MessageDialog("Please enable atoms in ePMV")
        else:
            main1(op)

    
if __name__=='__main__':
    main()