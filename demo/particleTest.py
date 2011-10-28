# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:29:11 2011

@author: -
"""
import c4d
epmv = c4d.mv.values()[0]
self = epmv.mv
coords = self.Mols[0].allAtoms.coords
PS = epmv.helper.particle(coords)
tpcnt = PS.NumParticles()
grp = PS.GetRootGroup()
particules = grp.GetParticles()
channelid = 0#epmv.helper.addDataChannel(PS,"shapeName",type="String")
sph = epmv.helper.getObject("1crn_b_cpk_shape")

cframe = doc.GetTime().GetFrame(doc.GetFps())
#PS = epmv.helper.getCurrentScene().GetParticleSystem()
if cframe != 0 :
    return

m = 0
coords = self.Mols[m].allAtoms.coords
name = self.Mols[m].name
PS = epmv.helper.particle(coords)
channelid = epmv.helper.addDataChannel(PS,"shapeName",type="String")
listeID = [i for i,at in enumerate(self.Mols[m].allAtoms) if at.name == "CA"]
epmv.helper.assignDataChannel(PS,channelid,listeID,[name+"_b_cpk_CA",])
listeID = [i for i,at in enumerate(self.Mols[m].allAtoms) if at.name[0] == "N"]
epmv.helper.assignDataChannel(PS,channelid,listeID,[name+"_b_cpk_N",])
listeID = [i for i,at in enumerate(self.Mols[m].allAtoms) if at.name[0] == "O"]
epmv.helper.assignDataChannel(PS,channelid,listeID,[name+"_b_cpk_O",])
listeID = [i for i,at in enumerate(self.Mols[m].allAtoms) if at.name[0] == "C"]
epmv.helper.assignDataChannel(PS,channelid,listeID,[name+"_b_cpk_C",])

for i,at in enumerate(self.Mols[0].allAtoms):
    if at.name == "CA":
        PS.SetPData(particules[i], channelid, i)

PSparent = epmv.helper.getObject("PS")
if PSparent is None :
    PSparent = epmv.helper.newEmpty("PS")
    epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),PSparent)

for i in [x for x in grp.GetParticles() if x<tpcnt]:
    uid = PS.GetPData(i, channelid)#returns an instance object of our shape
    sobj = epmv.helper.newInstance("pinstance"+str(i),
            object,location=None,c4dmatrice=None,matrice=None,
                    parent = None,material=None)
    #transfer the ID of the particle+1 to the IP of the object
    sobj.SetUniqueIP(i+1)
    
    #recieve the values of the particle
    #and calculate the matrix of the object
    lage = PS.Alignment(i)
    scale = PS.Scale(i)
    size  = PS.Size(i)

    # the size of a shape is calculated with
    # with the scale of the shape multiplied
    # with the scale of the particle multiplied
    # with an offset value called 'size'
#    size = shape.GetRelScale() ^ scale * size
#    scale = size / bboxsize
#    if scale==nv: continue

#    Scale(lage, scale.x, scale.y, scale.z)
    #transfer the particle pos to the shape pos
    
    lage = lage * sobj.GetMl()
    lage.off = PS.Position(i)

    #attach to the null list
    sobj.InsertUnderLast(null)
    sobj.SetMl(lage)