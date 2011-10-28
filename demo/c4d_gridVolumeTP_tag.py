# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:10:27 2011

@author: ludovic autin

python Tag for C4D, take the current PS that represent the grid points from ePMV data
if first frame generate the PS and set the Age
else overwrite the Age

"""


import c4d
#Welcome to the world of Python
import random
#BaseTime is in second

#Volume problem:
#value -> color            <=> age -> color
#value -> transparance     <=> age -> transparence

def main():
    epmv = c4d.mv.values()[0]
    grid = epmv.mv.grids3D.values()[0]#[name]how to specify it ... ? 
    #need  the particle aready created ...
    PS = doc.GetParticleSystem()
    root = PS.GetRootGroup()
    cframe = doc.GetTime().GetFrame(doc.GetFps()) #10->300,1->30
    #N = PS.NumParticles()
    #use the attached object/polygon to create the PS
    ob = op.GetObject()
    gname = "gridTP"
    maxi = grid.maxi #100%
    mini = grid.mini #0%
    #if grid.mini < 0 :
    #all value + abs(mini)
    #should we use color transfert map for getting Age ?
    N = grid.dimensions[0]*grid.dimensions[1]*grid.dimensions[2]
    print N
    lv = []
    for i in range(3) :  lv.append(grid.dimensions[i] * grid.stepSize[i])
    #Matrix[c4d.MG_GRID_SIZE]= epmv.helper.FromVec(lv)
    #Matrix[c4d.MG_GRID_RESOLUTION]= epmv.helper.FromVec(grid.dimensions)
    #ob is the matrix ?
    #trunk the data ? 
    NX,NY,NZ = grid.dimensions
    threshold = 100.0
    def returnW(i,j,k): return int(k*NX*NY + j*NX + i)
    #i,i,k -> w ? int(k*NX*NY + j*NX + i)
    if cframe == 0 :
        #generate the particle system for this group
#        v = ob.GetAllPoints()
#        N = len(v)
        ids = range(N)
        #gPS = epmv.helper.particle(gridPointsCoords,group_name=gname)
        life = [c4d.BaseTime(threshold),]*N
        map(PS.SetLife,ids,life)
        for i in range(NX):
            for j in range(NY):
                for k in range(NZ):
                    id=returnW(i,j,k)
                    val = grid.data[i][j][k]+mini
                    if val/maxi < threshold:
                        PS.SetAge(id,c4d.BaseTime(val))
                    else :
                        PS.SetAge(id,c4d.BaseTime(threshold))
        #ages = [c4d.BaseTime(d+mini) for d in dist]
        #map(PS.SetAge,ids,ages)
        #set up the Life and Age
    else :
        #data?
        for i in range(NX):
            for j in range(NY):
                for k in range(NZ):
                    id=returnW(i,j,k)
                    val = grid.data[i][j][k]+mini
                    if val/maxi < threshold:
                        PS.SetAge(id,c4d.BaseTime(val))
                    else :
                        PS.SetAge(id,c4d.BaseTime(threshold))
