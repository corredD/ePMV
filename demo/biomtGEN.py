# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 16:40:07 2011

@author: -
"""
#===============================================================================
# part1
#===============================================================================

import os
import numpy
from numpy.linalg import norm
from numpy import matrix
def getCenter(coords):
    """
    Get the center from a 3d array of coordinate x,y,z.

    @type  coords: liste/array
    @param coords: the coordinates

    @rtype:   list/array
    @return:  the center of mass of the coordinates
    """
    coords = numpy.array(coords)#self.allAtoms.coords
    center = sum(coords)/(len(coords)*1.0)
    center = list(center)
    for i in range(3):
        center[i] = round(center[i], 4)
#        print "center =", center
    return center

def getMat(_coords):
    v1=_coords[0]-_coords[1]
    v2=_coords[1]-_coords[2]
    v3 = numpy.cross(v1,v2)
    v3 = v3/norm(v3)
    v1 = numpy.cross(v3,v2)
    v1 = v1/norm(v1)
    v2 = v2 / norm(v2)
    c = getCenter(_coords) #offset
    mr=numpy.identity(4)
    mr[0,:3]=v1
    mr[1,:3]=v2
    mr[2,:3]=v3
    mr[3,:3]=c
    return mr
    
molname = "45C9C"#.pdb
#penta="fpen"#00
#hexa="hex"#000
dir="/Users/ludo/45C9C.pdb"
n=3
i=0
iMatrix=None#numpy.identity(4)
#iMatrixH=None#numpy.identity(4)
lMatrix=[]
#lMatrixH=[]
mol = self.readMolecule(dir)
#its actualy every two chains....

#do we need it for every chain
# or every unit 
for i,ch in enumerate(mol.chains):
    if i % 2  == 0:
        _coords=mol.chains[i:i+2].residues.atoms.coords
        _coords = numpy.array(_coords)
        #get the matrix,and the inverse for the first time.
        mr=getMat(_coords)
        if iMatrix is None :
            iMatrix = matrix(mr).I
            lMatrix.insert(0,iMatrix)
        lMatrix.append(matrix(mr))
        print i
rname="/Users/ludo/res.matrix"
numpy.save(rname,lMatrix)



import numpy
#===============================================================================
# part 2 
#===============================================================================
#UNCOMMENT
#import numpy
#rname="/Users/ludo/res.matrix"
#data1=numpy.load(rname+".npy")
#parent = epmv.helper.getObject("assambly")
#if parent is None :
#    parent = epmv.helper.newEmpty("assambly")
#    epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),parent)
#parent1 = epmv.helper.getObject("instance")
#if parent1 is None :
#    parent1 = epmv.helper.newEmpty("instance")
#    epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),parent1,parent=parent)
##    epmv.helper.reParent(parent1,parent)
#mx = epmv.helper.FromMat(data1[0],transpose=True)
#print mx
#epmv.helper.setObjectMatrix(parent1,hostmatrice=mx)
#
#hmat1 = [epmv.helper.FromMat(data1[i],transpose=False)*mx for i in range(1,len(data1))]
#pobj= epmv.helper.getObject("CoarseMS_tolun")
#ipoly = epmv.helper.instancePolygon("testP",matrices=data1[1:],mesh=pobj,globalT=False,
#                               parent = parent1,transpose=True)
#

#BIOMT GENERATION?
#REMARK 350   BIOMT1   1  1 0 0 0
#REMARK 350   BIOMT2   1  0 1 0 0
#REMARK 350   BIOMT3   1  0 0 1 0
#ToMat getTransformation
lmat = []
str=""
for j,p in enumerate(ipoly):
    m = epmv.helper.ToMat(epmv.helper.getTransformation(p))
    print m,m.shape
    lmat.append(m)
    for i in range(3):
#        print m[i][0],m[i][1],m[i][2],m[j][3]
        str+="REMARK 350   BIOMT%d  %2d  %.3f %.3f %.3f 0.\n" % (i+1,j+1,m[i][0],m[i][1],m[i][2])
f=open("/Users/ludo/res.matrix.biomt.txt","w")
f.write(str)
f.close()

import numpy
rname="/Users/ludo/res.matrix"
lmat = []
data1=numpy.load(rname+".npy")
str=""
str+="REMARK 350   BIOMT1   1  1 0 0 0\n"
str+="REMARK 350   BIOMT2   1  0 1 0 0\n"
str+="REMARK 350   BIOMT3   1  0 0 1 0\n"
from numpy import matrix
mx = matrix(data1[0])
for j,p in enumerate(data1[1:]):
    m = numpy.array(matrix(p)*mx)
    print m
    lmat.append(numpy.array(m))
    for i in range(3):
#        print m[i][0],m[i][1],m[i][2],m[j][3]
        str+="REMARK 350   BIOMT%d  %2d  %.3f %.3f %.3f %.3f\n" % (i+1,j+1,m[i][0],m[i][1],m[i][2],m[3][i])
f=open("/Users/ludo/res.matrix.biomt.numpy.txt","w")
f.write(str)
f.close()

import numpy
rname="/Users/ludo/res.matrix"
data1=numpy.load(rname+".npy")
mol = self.Mols[0]
vt=epmv.helper.ApplyMatrix(mol.allAtoms.coords,data1[0]) 
mol.allAtoms.updateCoords(vt,ind=0)

#import numpy
#rname="/Users/ludo/res.matrix"
#data1=numpy.load(rname+".npy")
#parent = epmv.helper.getObject("assambly")
#if parent is None :
#    parent = epmv.helper.newEmpty("assambly")
#    epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),parent)
#parent1 = epmv.helper.getObject("instance")
#if parent1 is None :
#    parent1 = epmv.helper.newEmpty("instance")
#    epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),parent1,parent=parent)
##    epmv.helper.reParent(parent1,parent)
#mx = epmv.helper.FromMat(data1[0],transpose=False)
#print mx
#epmv.helper.setObjectMatrix(parent1,hostmatrice=mx)
#
#hmat1 = [epmv.helper.FromMat(data1[i],transpose=False)*mx for i in range(1,len(data1))]
#pobj= epmv.helper.getObject("tolun")
#ipoly = epmv.helper.instancePolygon("testP",hmatrices=hmat1,matrices=data1[1:],mesh=pobj,globalT=False,
#                               parent = parent1,transpose=True)
##ipoly2 = helper.updateInstancePolygon("testP",None, hmatrices=hmat1,matrices=data2[1:], mesh=hobj,
##                              parent=parent1,transpose=False,globalT=True)

lmat = []
str=""
for j,p in enumerate(epmv.helper.getChilds(epmv.helper.getObject("Cloner"))):
    m = epmv.helper.ToMat(epmv.helper.getTransformation(p))
    print m,m.shape
    lmat.append(m)
    for i in range(3):
#        print m[i][0],m[i][1],m[i][2],m[j][3]
        str+="REMARK 350   BIOMT%d  %2d  %.3f %.3f %.3f %.3f\n" % (i+1,j+1,m[i][0],m[i][1],m[i][2],m[3][i])
f=open("/Users/ludo/res.matrix.array.txt","w")
f.write(str)
f.close()
