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

#volume 1
#density 0.1
#with MAtrix problem of particle position / grid position
#but creating the particle from the gris seems expansive ?
def main():
    epmv = c4d.mv.values()[0]
    grid = epmv.mv.grids3D.values()[0]#[name]how to specify it ... ? 
    N = grid.dimensions[0]*grid.dimensions[1]*grid.dimensions[2]
    print N    

    #root = PS.GetRootGroup()
    cframe = doc.GetTime().GetFrame(doc.GetFps()) #10->300,1->30
    if cframe == 0 :
        #make the PS
        PS = epmv.helper.grid_particle("grid",grid.dimensions,grid.getOriginReal(),grid.stepSize)
    #need  the particle aready created ...
    PS = doc.GetParticleSystem()    
    #N = PS.NumParticles()
    #use the attached object/polygon to create the PS
    ob = op.GetObject()
    gname = "gridTP"
    mean = grid.mean
    std = grid.std
    #need to normalize it 
#    diff = grid.maxi-grid.mini #maxi - mini

    maxi = grid.maxi#mean+std#grid.maxi #100%
    mini = grid.mini#mean-std#grid.mini #0%
    #normalized?
    diff = 0
    if mini < 0. :
        diff = maxi - mini #maxi - mini
    maxi = maxi + diff
    mini = mini + diff
    #grid.maxi+diff = 100%
    #if grid.mini < 0 :
    #all value + abs(mini)
    #should we use color transfert map for getting Age ?
    
    lv = []
    for i in range(3) :  lv.append(grid.dimensions[i] * grid.stepSize[i])
    #Matrix[c4d.MG_GRID_SIZE]= epmv.helper.FromVec(lv)
    #Matrix[c4d.MG_GRID_RESOLUTION]= epmv.helper.FromVec(grid.dimensions)
    #ob is the matrix ?
    #trunk the data ? 
    NX,NY,NZ = grid.dimensions
    threshold = maxi+0.1#is the maximum value of the data? or a thresh
    ids = range(N)
    def returnW(i,j,k): return int(k*NX*NY + j*NX + i)
    #i,i,k -> w ? int(k*NX*NY + j*NX + i)
    life = [c4d.BaseTime(threshold),]*N
    map(PS.SetLife,ids,life)
    for i in range(NX):
        for j in range(NY):
            for k in range(NZ):
                id=returnW(i,j,k)
                val = grid.data[i][j][k]+diff
                PS.SetAge(id,c4d.BaseTime(val))
                if val < maxi and val > mini :
                    PS.SetAge(id,c4d.BaseTime(val))
                elif val >= maxi  :
                    PS.SetAge(id,c4d.BaseTime(maxi))
                elif val <= mini  :
                    PS.SetAge(id,c4d.BaseTime(mini))
