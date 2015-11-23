
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/uv_test.py is part of ePMV.

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
import math
surfName="CoarseMS_ind"
mol = epmv.gui.current_mol
surf = mol.geomContainer.geoms[surfName]
vertices=surf.getVertices()
faces=surf.getFaces()
colors=mol.geomContainer.getGeomColor(surf) #per vertex of per face...msms is per vertex
if colors is None :
    if surfName in mol.geomContainer.atomPropToVertices:
        func = mol.geomContainer.atomPropToVertices[surfName]
        geom = mol.geomContainer.geoms[surfName]
        atms = mol.geomContainer.atoms[surfName]
        colors = func(geom, atms, 'colors', propIndex=surfName)
surfobj = epmv.helper.getObject(surf.obj)

print(len(faces), math.sqrt(len(faces)))
s=20
sizex= math.sqrt(len(faces))*(s+1)
sizey = math.sqrt(len(faces))*(s+1)
print((sizex, sizey))

#mat = epmv.helper.createTexturedMaterial(surfName+"UV","/Users/ludo/uv.png")
#epmv.helper.assignMaterial(mat,surfobj,texture=True)
epmv.helper.makeTexture(surfobj,filename="/Users/ludo/uv.png",colors=colors,
                        sizex=sizex,sizey=sizey,faces=faces,
                        s=s,draw=True,invert=True) #maya need inversion.
                        
#if uv already exist from automatic unwrapping :
epmv.helper.makeTextureFromUVs(surfobj,filename="/Users/ludo/uv.png",colors=colors,
                        sizex=sizex,sizey=sizey,
                        s=s,draw=True,invert=False)
import c4d
import maya
from maya import cmds
import maya.OpenMaya as om
import math
#what about using a ramp?
x=0
y=0
s=20
surfobj = epmv.helper.getObject(surf.obj)
node = epmv.helper.getNode('mesh_'+surf.obj)
meshnode = om.MFnMesh(node)

print(len(faces), math.sqrt(len(faces)))
sizex= math.sqrt(len(faces))*(s+1)
sizey = math.sqrt(len(faces))*(s+1)
print((sizex, sizey))
im = Image.new("RGB", (sizex, sizey),(0, 0, 0))
imdraw = ImageDraw.Draw(im)

tag =surfobj.GetTags()[2]
uv = numpy.zeros((len(vertices),2))#its a % but why
listexyz=[]
listecolor=[]

def myfunc3(f,colors,x,y,s):
    def uvs(a,xys):
        return (xys[0][0]+a[0],xys[0][1]+a[1])
    
    def cols(a,n,col1,col2,col3):
        return (col1+(a[1]/n)*(col3-col1))+(a[0]/n)*(col2-(col1+(a[1]/n)*(col3-col1)))
    xys = [(x,y),(x+s,y+s),(x+s,y)]
    col1=numpy.array(epmv.helper.convertColor(colors[f[0]]))
    col2=numpy.array(epmv.helper.convertColor(colors[f[1]]))
    col3=numpy.array(epmv.helper.convertColor(colors[f[2]]))
    ii,jj=numpy.mgrid[:20,:20]
    couples = numpy.vstack((ii.flatten(),jj.flatten())).transpose()    
    uv = numpy.apply_along_axis(uvs, 1, couples,xys) #create uvcoords
    cols = numpy.apply_along_axis(cols, 1, couples,20.,col1,col2,col3) #create color gradiant
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
    return uvs,cols

res = numpy.apply_along_axis(myfunc3, 1,numpy.array(faces,int),colors,x,y,s) #create uvcoords
print(res)
def interpolateCOL(a,col1,col2,col3):
    xcol = col1+a[0]*(col3-col1)
    ycol = xcol+a[1]*(col2-xcol)
    return ycol.tolist()

def drawGradientLine(col1,col2,col3,xys):
    if col1 is col2 and col2 is col3 :
#        imdraw.polygon(xys, fill=(col1[0], col1[1], col1[2]))
        imdraw.rectangle([xys[0],xys[1]], fill=(col1[0], col1[1], col1[2]))
    else:
        for i in range(20):
            a=i/20.
            for j in range(20):
                b = j/20.
#                imdraw.line((xys[0][0],xys[0][1]+20*a,xys[1][0],xys[0][1]+20*a), 
#                col=(c[0]+a*(col3[0]-c[0]),c[1]+a*(col3[1]-c[0]),c[2]+a*(col3[2]-c[2]))#linear interpolation
                #need to draw a 20*20 points array
                xy = (xys[0][0]+j,xys[0][1]+i)
                xcol = col1+b*(col3-col1)
                ycol = xcol+a*(col2-xcol)
#                ycol = interpolateCOL((a,b),col1,col2,col3)
                imdraw.point((xys[0][0]+j,xys[0][1]+i),fill=(ycol[0],ycol[1],ycol[2]))
import time
t1=time.time()
for i,f in enumerate(faces) :
    xys = [(x,y),(x+s,y+s),(x+s,y)]
    box= [(x,y),(x+s,y+s)]
   # print xys
    c1=numpy.array(epmv.helper.convertColor(colors[f[0]]))
    c2=numpy.array(epmv.helper.convertColor(colors[f[1]]))
    c3=numpy.array(epmv.helper.convertColor(colors[f[2]]))
#    c=epmv.helper.convertColor(colors[f[2]])
#    c=numpy.average(numpy.array([c1,c2,c3]),axis=0)
#    listecolor.append(c)
#    imdraw.polygon(xys, fill=(c[0], c[1], c[2]))
    #rectangle need (x1, y1), (x2, y2)
    drawGradientLine(c1,c2,c3,xys)
#    imdraw.rectangle(box, fill=(c[0], c[1], c[2]))
#    if uv[f[0]][0] ==0 and uv[f[0]][1]==0:
#    uv[f[0]] = (x,y)
##    if uv[f[1]][0] ==0 and uv[f[1]][1]==0:
#    uv[f[1]] = (x+s,y+s)
##    if uv[f[2]][0] ==0 and uv[f[2]][1]==0:
#    uv[f[2]] = (x+s,y)
#    listexyz.append(xys)
    #next one
    tag.SetSlow(i, c4d.Vector((x+2)/sizex,(y+2)/sizey,0), 
                c4d.Vector((x+s-2)/sizex,(y+s-2)/sizey,0), 
                c4d.Vector((x+s-2)/sizex,(y+2)/sizey,0), 
                c4d.Vector((x+s-2)/sizex,(y+2)/sizey,0))

    u[f[0]]=(x+2)/sizex
    u[f[1]]=(x+s-2)/sizex
    u[f[2]]=(x+s-2)/sizex
    v[f[0]]=(y+2)/sizey
    v[f[1]]=(y+s-2)/sizey
    v[f[2]]=(y+2)/sizey    
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
   # if y >=sizey or y+s >sizey:
        #break
x=0
y=0
s=20.
for i,f in enumerate(faces) :

    u.set((x+2)/sizex,int(f[0]))
    u.set((x+s-2)/sizex,int(f[1]))
    u.set((x+s-2)/sizex,int(f[2]))
    v.set((y+2)/sizey,int(f[0]))
    v.set((y+s-2)/sizey,int(f[1]))
    v.set((y+2)/sizey ,int(f[2]))
    meshnode.setUV(Ids[0],(x+2)/sizex,(y+2)/sizey)    
    meshnode.setUV(Ids[1],(x+s-2)/sizex,(y+s-2)/sizey)    
    meshnode.setUV(Ids[2],(x+s-2)/sizex,(y+2)/sizey)    
    
    for j in range(3):
        meshnode.assignUV(i,int(f[j]),int(f[j])) 
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
meshnode.setUVs(u,v)
uvIds = om.MIntArray() 
for f in faces:
    for i in f : 
        uvIds.append(int(i))
uvCounts = om.MIntArray()    
for c in range(0,len(faces),1):
    uvCounts.append(int(len(f)))
meshnode.assignUVs(uvCounts,uvIds)
print("TIME ",time.time() -t1)
listecolor = numpy.array(listecolor)
for l in range(100):
    colour = (0, 0, 255 * l / 100)
    imdraw.line((0, l, 100, l), fill=colour)#line are xy->xy
del imdraw
import ImageOps
im=Image.open("/Users/ludo/uv.png")
imo=ImageOps.mirror(im)
im=ImageOps.flip(imo)
im.save("/Users/ludo/uv.png")
#53
#56
#75
#C4D
#    tag.SetSlow(i, c4d.Vector((x+2)/sizex,(y+2)/sizey,0), 
#                c4d.Vector((x+s-2)/sizex,(y+s-2)/sizey,0), 
#                c4d.Vector((x+s-2)/sizex,(y+2)/sizey,0), 
#                c4d.Vector((x+s-2)/sizex,(y+2)/sizey,0))
x=0
y=0
s=20
u = om.MFloatArray(len(vertices))
v = om.MFloatArray(len(vertices))
#meshnode.setUVs(u,v)
Ids = om.MIntArray()
uvIds = om.MIntArray()
uvCounts = om.MIntArray()
for i,f in enumerate(faces) :
    print((x+2)/sizex,(y+2)/sizey,(x+s-2)/sizex,(y+s-2)/sizey,(x+s-2)/sizex,(y+2)/sizey)
    meshnode.getPolygonVertices(i,Ids)
    uvl = [[(x+2)/sizex,(y+2)/sizey],[(x+s-2)/sizex,(y+s-2)/sizey],[(x+s-2)/sizex,(y+2)/sizey]]
    #uvl=((0,0.1),(0.1,0.1),(0.1,0.1))
    #print Ids 
    uvCounts.append(int(len(f)))
    for j,ind in enumerate(Ids):
        #print i,ind
        if u[ind] == 0 :  
            u.set(uvl[j][0],ind)
        if v[ind] == 0 :  
            v.set(uvl[j][1],ind)
        uvIds.append(ind)
#        meshnode.setUV(ind,uvl[j][0],uvl[j][1])
        #meshnode.assignUV(i,int(ind),int(ind))    meshnode.getPolygonUVid(i,Ids[2])
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
    if i == 23:
        break
meshnode.setUVs(u,v)
meshnode.assignUVs(uvCounts,uvIds)
def interpolateCOL(a,col1,col2,col3):
    xcol = col1+a[0]*(col3-col1)
    ycol = xcol+a[1]*(col2-xcol)
    return ycol.tolist()
    
def drawPtCol(uvs,c0,c1,c2):
    u=uvs[0][0]
    v=uvs[0][1]
    
    du01 = uvs[0][0] - uvs[1][0]
    du12 = uvs[1][0] - uvs[2][0]
    du02 = uvs[0][0] - uvs[2][0]
    dv01 = uvs[0][1] - uvs[1][1]
    dv12 = uvs[1][1] - uvs[2][1]
    dv02 = uvs[0][1] - uvs[2][1]
    distu = [[0.,du01,du02],[-du01,0.,du12],[-du02,-du12,0.]]
    distv = [[0.,dv01,dv02],[-dv01,0.,dv12],[-dv02,-dv12,0.]]
    #imdraw.point((u,v))
    #nexpoint
    #draw the one on left- fraw left to right
    order=[0,1,2]
    color = [c0,c1,c2] 
    if du01 < 0 and du02 < 0 : 
        if du01 < du02 :
            order=[0,2,1]
        else :
            order=[0,1,2]
    elif -du12 < 0 and -du02 < 0 :
        if -du12 < -du02 :
            order=[2,0,1]
        else :
            order=[2,1,0]
    elif -du01 < 0 and du12 < 0 :
        if -du01 < du12 :
            order=[1,2,0]
        else :
            order=[1,0,2]
    u = uvs[order[0]][0] 
    v = uvs[order[0]][1]
    imdraw.point((u,v))
    #nexpoint
    i = 0
    du=distu[order[0]][order[1]]
    dvb = distv[order[0]][order[0]]
    dvt = distv[order[0]][order[1]]
    if dvb < dvt :
        #check sign
        a=(v - dvb*i/dvb)
        b=(v + dvt*i/dvt)
    else :
        b=(v - dvb*i/dvb)
        a=(v + dvt*i/dvt)
    changeab=False
    for i in range(20):
        #u u + 1 i start at 0
        u = u + du*i/du
        n = len(list(range(a,b)))
        for j in range(a,b):
            print(u,j)
            xcol = color[order[0]]+i/20.*(color[order[1]]-color[order[0]])
            ycol = xcol+j/n*(color[order[2]]-xcol)            
            imdraw.point((u,j),fill=(ycol[0],ycol[1],ycol[2]))
            if j == uvs[order[1]][1] : 
                #need to change a,b
                changeab = True
#                v = uvs[order[1]][1]
        if changeab :
            dvb = distv[order[1]][order[1]]
            a=(uvs[order[1]][1] - dvb*i/dvb)
            b=(v + dvt*i/dvt)
        else :
            a=(v - dvb*i/dvb)
            b=(v + dvt*i/dvt)
            
        
#imdraw.point((u,v),fill=(ycol[0],ycol[1],ycol[2]))
#select all faces
#automatic Projection in polygon option
surfName="CoarseMS_ind"
mol = epmv.gui.current_mol
surf = mol.geomContainer.geoms[surfName]
vertices=surf.getVertices()
faces=surf.getFaces()
colors=mol.geomContainer.getGeomColor(surf) #per vertex of per face...msms is per vertex
if colors is None :
    if surfName in mol.geomContainer.atomPropToVertices:
        func = mol.geomContainer.atomPropToVertices[surfName]
        geom = mol.geomContainer.geoms[surfName]
        atms = mol.geomContainer.atoms[surfName]
        colors = func(geom, atms, 'colors', propIndex=surfName)
import numpy
import Image
import ImageDraw
import maya
from maya import cmds
import maya.OpenMaya as om
import math
#what about using a ramp?
x=0
y=0
s=20
surfobj = epmv.helper.getObject(surf.obj)
node = epmv.helper.getNode('mesh_'+surf.obj)
meshnode = om.MFnMesh(node)
print(len(faces), math.sqrt(len(faces)))
sizex= math.sqrt(len(faces))*(s+1)
sizey = math.sqrt(len(faces))*(s+1)


Ids = om.MIntArray()
u = om.MScriptUtil()
u.createFromDouble(0.)
ptru = u.asFloatPtr()
v = om.MScriptUtil()
v.createFromDouble(0.)
ptrv = v.asFloatPtr()
im = Image.new("RGB", (sizex, sizey),(0, 0, 0))
imdraw = ImageDraw.Draw(im)
uv = numpy.zeros((len(vertices),2))
uu = om.MFloatArray()
vv = om.MFloatArray()
#uu = om.MIntArray()3
#vv = om.MIntArray()
meshnode.getUVs(uu,vv)
uuvv = numpy.vstack((numpy.array(uu)*sizex,numpy.array(vv)*sizex)).transpose()
im = Image.new("RGB", (sizex, sizey),(0, 0, 0))
imdraw = ImageDraw.Draw(im)
imdraw.line((sizex-uuvv).flatten().tolist())
im.save("/Users/ludo/uv.png")
uvs=[]
triuvs=[]
im = Image.new("RGB", (sizex, sizex),(0, 0, 0))
imdraw = ImageDraw.Draw(im)
itPoly = om.MItMeshPolygon( meshnode.object() )
while not itPoly.isDone():
    # Get UVs
    print(itPoly.index())
    f = faces[itPoly.index()]
    faceU = om.MFloatArray()
    faceV = om.MFloatArray()
    itPoly.getUVs( faceU, faceV )
    uvs=[]
    color = []
    for i in range( faceU.length() ):
        print("vi",itPoly.vertexIndex(i))
        vi = itPoly.vertexIndex(i)
        color.append(epmv.helper.convertColor(colors[vi]))
        uvs.append( [faceU[i]*sizex, (1-(faceV[i]))*sizex] )#order?
#    triuvs.append(uvs)
#    c0=numpy.array(epmv.helper.convertColor(colors[f[0]]))
#    c1=numpy.array(epmv.helper.convertColor(colors[f[1]]))
#    c2=numpy.array(epmv.helper.convertColor(colors[f[2]]))
    drawPtCol(numpy.array(uvs),numpy.array(color))
    #imdraw.polygon(numpy.array(uvs,int).flatten().tolist())
    #triuvs.append(uvs)
    if itPoly.index() == 0:
        break
    next(itPoly)
im.save("/Users/ludo/uv.png")
x=0
y=0
s=20.
itPoly = om.MItMeshPolygon( meshnode.object() )
u = om.MScriptUtil()
u.createFromDouble(0.)
ptru = u.asFloatPtr()
v = om.MScriptUtil()
v.createFromDouble(0.)
ptrv = v.asFloatPtr()
uv = om.MScriptUtil()
uv.createFromDouble(0.,0.)
ptruv = u.asFloat2Ptr()
while not itPoly.isDone():
    f = faces[itPoly.index()]
    uv.setFloat2ArrayItem(ptruv,0,1,(x+2.)/sizex)
    uv.setFloat2ArrayItem(ptruv,0,2,1-(y+2.)/sizey)
    itPoly.setUV(f[0],ptruv)    
    uv.setFloat2ArrayItem(ptruv,0,1,(x+s-2.)/sizex)
    uv.setFloat2ArrayItem(ptruv,0,2,1-(y+s-2.)/sizey)
    itPoly.setUV(f[1],ptruv)    
    uv.setFloat2ArrayItem(ptruv,0,1,(x+s-2.)/sizex)
    uv.setFloat2ArrayItem(ptruv,0,2,1-(y+2.)/sizey)
    itPoly.setUV(f[2],ptruv)    
##    itPoly.setUV(f[1],(x+s-2.)/sizex,(y+s-2.)/sizey)    
#    itPoly.setUV(f[2],(x+s-2.)/sizex,(y+2.)/sizey)    
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
    next(itPoly)
    
uvs = numpy.array(numpy.array(triuvs)*sizex,int)
im.save("/Users/ludo/uv.png")
im = Image.new("RGB", (sizex, sizex),(0, 0, 0))
imdraw = ImageDraw.Draw(im)
for i,f in enumerate(faces[0:1]) :
    c0=numpy.array(epmv.helper.convertColor(colors[f[0]]))
    c1=numpy.array(epmv.helper.convertColor(colors[f[1]]))
    c2=numpy.array(epmv.helper.convertColor(colors[f[2]]))
#    #try line to debug
#    imdraw.point(numpy.array(uv,int).flatten().tolist())
#    imdraw.polygon(numpy.array(uv,int).flatten().tolist())
    print(uvs[i])
    drawPtCol(numpy.array(uvs[i],int),c0,c1,c2)
im.save("/Users/ludo/uv.png")

Ids = om.MIntArray()
u = om.MScriptUtil()
u.createFromDouble(0.)
ptru = u.asFloatPtr()
v = om.MScriptUtil()
v.createFromDouble(0.)
ptrv = v.asFloatPtr()
sizex=2000
im = Image.new("RGB", (sizex, sizex),(0, 0, 0))
imdraw = ImageDraw.Draw(im)
liste=[]
for i,f in enumerate(faces[0:1]) :#[0:10]
    meshnode.getPolygonVertices(i,Ids)
    uv = numpy.zeros((3,2))
    print(Ids)
    for j,ind in enumerate(Ids): 
        meshnode.getUV(ind,ptru,ptrv)
        print(u.getFloat(ptru),v.getFloat(ptrv))
        uv[j]=numpy.array([u.getFloat(ptru)*sizex,sizex-(v.getFloat(ptrv)*sizex)],int)
#    print uv
    liste.append(uv)
#    uv[3] = uv[0]
#    print uv
    c0=numpy.array(epmv.helper.convertColor(colors[f[0]]))
    c1=numpy.array(epmv.helper.convertColor(colors[f[1]]))
    c2=numpy.array(epmv.helper.convertColor(colors[f[2]]))
#    #try line to debug
#    imdraw.point(numpy.array(uv,int).flatten().tolist())
#    imdraw.polygon(numpy.array(uv,int).flatten().tolist())
    drawPtCol(numpy.array(uv,int),c0,c1,c2)
im.save("/Users/ludo/uv.png")




faces = epmv.helper.getFaces(surfobj)
x=0
y=0
s=s
uv={}
for i,f in enumerate(faces) :
    xys = [(x,y),(x+s,y+s),(x+s,y)]
    box= [(x,y),(x+s,y+s)]
    #c1=numpy.array(epmv.helper.convertColor(colors[f[0]]))
    #c2=numpy.array(epmv.helper.convertColor(colors[f[1]]))
    #c3=numpy.array(epmv.helper.convertColor(colors[f[2]]))
    #if draw :
    #    self.drawGradientLine(imdraw,c1,c2,c3,xys)
        #self.drawPtCol(imdraw,numpy.array([c1,c2,c3]),xys,debug=0)
    uv[i]=[[(x+2)/sizex,(y+2)/sizey,0], 
                    [(x+s-2)/sizex,(y+s-2)/sizey,0], 
                    [(x+s-2)/sizex,(y+2)/sizey,0],
                    [(x+s-2)/sizex,(y+2)/sizey,0]]
    x = x + s
    if x >=sizex or x +s >=sizex:
        x = 0
        y = y + s
        
        
self.setUVs(object,uv)
img.save(filename)
self.resetProgressBar(0)
