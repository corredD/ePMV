# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:33:29 2011

@author: -
"""
from ePMV.molAdaptor import molAdaptor,aGeom
import yasara
import os
import numpy
import math

class yasaraAdaptor(molAdaptor):
    def start_engine(self,):
        yasara.info.mode='txt'
        yasara.CoordSys = 'right'
        self.cmd = yasara
        self.center_mol = 1
        return yasara
    
    def Load(self,filename,name,center=1):
        obj = self.cmd.LoadPDB(filename,center=center)
        #self.cmd.PosObj(name,0.,0.,-50.0)
        self.center_mol = center
        return obj
    
    def readMolecule(self,filename,name=None,center=1):
        if name is None :
            name = filename.split('/')[-1].split('.')[0]
        o=self.Load(filename,name,center=center)
        self.Mols[name]={}
        self.center_mol = center
        return name

    def displayExtrudedSS(self,name,fancyH=True,color="",typeSS="Cartoon"):#Ribbon,Tube
        #color "ss"
        #self.cmd.hide("all")
        self.cmd.HideAll()
        res=self.cmd.ShowSecStrObj(name,typeSS)
        geom = self.parsePOVmesh2(name)
        return geom

    def get_povray(self):
        self.cmd.SavePOV("tmp.pov")
        path=yasara.PWD()
        povname = path+os.sep+"tmp.pov"
        f = open(povname,"r")
        lines = f.readlines()
        f.close()
        return lines

    def get_view(self):
        return [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]


    def parseVectors(self,lines,l):
        nvector= int(lines[l].split("{")[1][:-2])
        vector=[[None,None,None],]*nvector
        l=l+1
        k=0
        i=0
        done = False
        while not done :
        #for i in range(nvector/4):#number of lines
            slines = lines[l+i].split("<")
            #if lines[l+i].find("texture_list") != 0 or lines[l+i].find("normal_vector") != 0  :
            #    done = True
            #    i = i - 2
            #    break                
            if len(slines) <= 1 :
                done = True
                if lines[l+i].find("texture_list") != -1 or lines[l+i].find("normal_vector") != -1  :
                    i = i - 2
                else :
                    i = i - 1
                break
            for j in range(1,len(slines)-1):
               vliste =  slines[j][:-2].split(",")
               vector[k] =[float(v) for v in vliste]
               k = k + 1
            vliste =  slines[len(slines)-1][:-3].split(",")
            vector[k] =[float(v) for v in vliste]
            k = k + 1
            i = i +1
        return vector,i               

    def parseVectorsF(self,lines,l):
        nvector= int(lines[l].split("{")[1][:-2])
        vector=[[None,None,None],]*nvector
        l=l+1
        k=0
        for i in range(nvector/7):#number of lines
            print lines[l+i]        
            slines = lines[l+i].split(">,")#ca have ,2, ,3,
            print slines
            if len(slines) <= 1 :
                break
            for j in range(len(slines)-1):
               vliste =  slines[j].split("<")[1].split(",")
#               print vliste
               vector[k] =[int(v) for v in vliste]
               k = k + 1
        return vector,i        

    def parseVectorsFcolor(self,lines,l,color):
        nvector= int(lines[l].split("{")[1][:-2])
        print nvector        
        colors=[[None,None,None],]*nvector
        vector=[[None,None,None],]*nvector
        l=l+1
        k=0
        i=0
        done = False
        while not done:        
        #for i in range(nvector/7):#number of lines
            #print lines[l+i]        
            slines = lines[l+i].split("<")#ca have ,2, ,3,
            #print slines
            if lines[l+i].find("mesh") != -1:
                print "##############",i
                done = True
                i = i - 1
                break
            if len(slines) <= 1 :
                print "##############",i
                done = True
                break
            for j in range(1,len(slines)):
               vliste =  slines[j].split(">")[0].split(",")
               coli = int(slines[j].split(">")[1].replace(",","").replace("}","")[0])#mix vColor anf fColor
               colors[k] =  color[coli]
               vector[k] = [int(v) for v in vliste]
               k = k + 1
#            print i,k,len(slines)-1
            i=i+1
        return vector,colors,i        
        
    def parseVectorsT(self,lines,l):
        nvector= int(lines[l].split("{")[1][:-2])
        vector=[None,]*nvector
        l=l+1
        k=0
        for i in range(int(math.ceil(nvector/3.))):#number of lines
            slines = lines[l+i].split("texture{")
            for j in range(1,len(slines)-1):
               vliste =  slines[j][:-2].split(",")[0]
               vector[k] =self.rgb(vliste.split("Col")[1])#vliste#[float(v) for v in vliste]
               k = k + 1
            vliste =  slines[len(slines)-1][:-3].split(",")[0][:-1]
            vector[k] = self.rgb(vliste.split("Col")[1])#[float(v) for v in vliste]
            k = k + 1
            
        return vector,i        

    def parseVectorsN(self,lines,l,vertex):
        vector=[]
        newv=[]
        colors = []
        newFaces=[]
        vnormal=[]
        done = False
        k=0
        i=0
        while not done :
            #print lines[l+i]        
            slines = lines[l+i].split("<")#ca have ,2, ,3,
            #print slines
            if len(slines) <= 1 :
                done = True                
                break        
            f1=[]
            f2=[]
            for j in range(1,len(slines)):
               vliste =  slines[j].split(">")[0].split(",")
               #print vliste
               vec =[float(v) for v in vliste]
               if j % 2 == 1 : #vertice
                   try :
                       fi=vertex.index(vec)
                   except :
                       vertex.append(vec)
                       fi = len(vertex)-1
                   #vector.append(vec)
#                   if len(f1) < 3:
                   f1.append(fi)
#                   else :
#                       f2.append(fi
               else : #vnormal
                   pass
               k = k + 1
            newFaces.append(f1)            
            #col
            try :
                col = slines[6].split("texture{")[1].split("}")[0].split("Col")[1]
            except :
                col = slines[6].split("texture_list{")[1].split(",")[0].split("Col")[1]
            colors.append(self.rgb(col)) 
            i = i + 1
        return vertex,newFaces,colors,i 

    def rgb(self,c):
        split = (c[0:2], c[2:4], c[4:6])
        return [int(x, 16) for x in split]
    
    def parsePOVmesh2(self,name,rep="cartoon"):
        #undisplay everything
        self.viewmat = self.get_view()        
        #display only name in representation rep
        lines = self.get_povray()
        done = False
        vertices=[]
        faces=[]
        normals=[]
        colors=[]
        #perface dictionary local indice to general indice
        l = 0
        first = True
        while not done:
            #getVertices
            if lines[l].find("mesh2") >=0 :
                l=l+1                
                localToglobal={}
                if lines[l].find("vertex_vectors") >= 0:
                    #'vertex_vectors { 4008,\n'
                    vertex,i  = self.parseVectors(lines,l)                     
                    l=l+i+3
                if lines[l].find("normal_vectors") >= 0:                  
                    normal,i =self.parseVectors(lines,l)        
                    if self.debug:
                        print("normal",normal)
                    l=l+i+3
                if lines[l].find("texture_list") >= 0:
                    color,i = self.parseVectorsT(lines,l)
                    l=l+i+2
                if lines[l].find("face_indices") >= 0:
                    #local face order
                    #'<0,4,1>,1,<1,4,12>,1,<1,12,5>,1,<5,12,24>,1,<5,24,13>,1,<17,18,8>,1,<8,18,9>,1,\n'
                    local,col,i = self.parseVectorsFcolor(lines,l,color)
                    #localface = [int(f) for f in local]
                    l=l+i+2
                #now N-Gons as smooth_triangle in mesh keyword
                if lines[l].find("mesh") >= 0:
                    l  = l + 1
                    if lines[l].find("smooth_triangle") >= 0:
                        vertex,ngons,c,i = self.parseVectorsN(lines,l,vertex)
                        l=l+i+2
                #ok now i should have the complete face, I can check                
                normals.extend(normal)
                vertices.extend(vertex)
                faces.extend(local)
                faces.extend(ngons)
                colors.extend(col)
                colors.extend(c)
                first = False
            else :
                l = l +1
            if l >= len(lines)-1 :
                done = True
                break                        
            #elif self.debug :
            #    print(l,lines[l])
        if self.debug:
            print(len(normals),normals[3])
        #transformation = self.viewmat[9:12]-self.viewmat[12:15]
        scale = 0.01*0.95       
#        vertices = numpy.array(vertices) - numpy.array([0.0,0.0,50.0])
        #-42.0,9.869,9.193
        vertices = numpy.array(vertices) - numpy.array([0.,0.,50*1./scale]) 
        vertices = vertices * numpy.array([-scale,scale,scale])# transformation
        return aGeom(vertices=vertices,faces=faces,
                        normals=numpy.array(normals),
                        colors=numpy.array(colors))                

#how to
#build a mesh
#from ePMV.extension.yasaraAdaptor import yasaraAdaptor;y = yasaraAdaptor();r=y.readMolecule("/Users/ludo/1crn.pdb",center=0);y.debug = 1;geom=y.displayExtrudedSS(r,typeSS="Tube")
#y = yasaraAdaptor()
#r=y.readMolecule("/Users/ludo/1crn.pdb")
#geom=y.displayExtrudedSS(r)
#make the geom now ....maybe problem of scale 
#import c4d;epmv = c4d.mv.values()[0];obj=epmv.helper.createsNmesh(r+"cartoon",geom.vertices,geom.normals,geom.faces,proxyCol=True)
#epmv.helper.changeColor(obj[0],geom.colors,pb=False)