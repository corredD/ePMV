# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 14:49:43 2012

@author: Ludovic Autin
"""
import os
import sys
try :
    import urllib.request as urllib# , urllib.parse, urllib.error
except :
    import urllib

try :
    import requests
except :
    request = None
    #fetch request module
    import Pmv
    import tarfile
    import shutil        
    patchpath = Pmv.__path__[0]
    os.chdir(patchpath)
    os.chdir("../")
    patchpath = os.path.abspath(os.curdir)
    URI="http://mgldev.scripps.edu/projects/ePMV/SOURCES/PMV/requests.tar"
    tmpFileName = patchpath+os.sep+"requests.tar"
#    if not os.path.isfile(tmpFileName):
    urllib.urlretrieve(URI, tmpFileName)
    TF=tarfile.TarFile(tmpFileName)
    dirname1=patchpath+os.sep+"requests"
    if os.path.exists(dirname1):
        shutil.rmtree(dirname1,True)           
    TF.extractall(patchpath)
#    os.remove(tmpFileName)
    try :
        import requests
    except :
        request = None
        print ("probleme downloading requests module")
    
from Pmv.mvCommand import MVCommand
class BuildDNACommand(MVCommand):
    """The BuildDNACommand class is the base class to build a DNA structure from a  sequence.
    \nPackage : Pmv
    \nModule  : colorCommands
    \nClass   : ColorCommand
    \nCommand : color
    \nDescription:\n
    It implements the general functionalities to color the specified geometries
    representing the specified nodes with the given list of colors.\n
    \nSynopsis:\n
      None <--- color(nodes, colors[(1.,1.,1.),], geomsToColor='all', **kw)\n
    \nRequired Arguments:\n 
      nodes --- any set of MolKit nodes describing molecular components\n
    \nOptional Arguments:\n  
      colors --- list of rgb tuple\n
      geomsToColor --- list of the name of geometries to color default is 'all'\n
      Keywords --- color\n
    """
    undoStack = []
    def __init__(self, func=None):
        MVCommand.__init__(self, func)
        self.flag = self.flag | self.objArgOnly
        self.options= {"fiberform":"M1"}#default options
        self.postdicionary={}

    def onAddCmdToViewer(self):
        # this is done for sub classes to be able to change the undoCmdsString
        self.undoCmdsString = self.name
        
    def onRemoveObjectFromViewer(self, object):
        self.cleanup()
    
    def onAddObjectToViewer(self, object):
        self.cleanup()
        
    def getPath(self,htmlstring):
        lines = htmlstring.split("\n")
        path=""
        for l in lines:
            if l.find('name="path"') != -1 :
                line =l.split()
                for i,s in enumerate(line) :
                    if s=='name="path"' :
                        path = line[i+1].split("=")[1]
                        break
                break
        return path
        
    def doit(self, fname, seq, **kw):
        print( fname)
        print("%s" % seq)
        self.postdicionary= {'fiberform':'M1','submit':'Continue'}
        #setup the session
        r = requests.post("http://w3dna.rutgers.edu/rebuild/fiberch", data=self.postdicionary)
        path  = self.getPath(r.text)
        #path is the temproary path on the w3dna server
        #get the form
        fiberform=self.options["fiberform"]
        if "fiberform" in kw :
            fiberform=kw["fiberform"]
        if not len(path) : return
        
        self.postdicionary = {'seq': seq, 'dnaform':fiberform,'fiberform':fiberform,'submit':'Build',"path":path,"block":False}
        #ask the server to build the DNA structure
        r = requests.post("http://w3dna.rutgers.edu/rebuild/regseq", data=self.postdicionary)
        #get the builded DNA from the server temporar path
        pathTo=None 
        if "path" in kw:
            pathTo=kw["path"]        
        name,pathTo=self.retrieveDNAPDBonServer(path,name=fname,pathTo=pathTo)  
        if name is None :
            print ("Error whle fetching the builded DNA")
        if "load" in kw :
            if kw["load"]:
                self.vf.readMolecule(pathTo+name)#is this will ensureepmv to update?
        return name, pathTo
        
    def retrieveDNAPDBonServer(self,path,name=None,pathTo=None):
        done = False
        cut= 0
        dnafile = None
        print ("http://w3dna.rutgers.edu/"+path[1:-1]+"/s0.pdb")
        if name is None :
            name = "s0.pdb"
        if pathTo is None :
            pathTo = self.vf.rcFolder+os.sep+"pdbcache"+os.sep 
        tmpFileName =  pathTo+name   
        while not done :
            if cut > 100 :        
                break
            try :
#                dnafile = urllib2.urlopen("http://w3dna.rutgers.edu/data/usr/"+path+"/rebuild/s0.pdb")
#                dnafile = urllib2.urlopen("http://w3dna.rutgers.edu/"+path[1:-1]+"/s0.pdb")
                urllib.urlretrieve("http://w3dna.rutgers.edu/"+path[1:-1]+"/s0.pdb", tmpFileName)
                done = True
            except :
                cut+=1        
                continue
        if done :
            #should download in the  rcFolder
#
#            output = open(pathTo+name,'w')
#            output.write(dnafile.read())
#            output.close()
            return name,pathTo
        return None,None


    def __call__(self, name, seq, **kw):
        """None <--- buildDNA(name,seq,**kw)
        \nnodes---TreeNodeSet holding the current selection
        \ncolors---list of rgb tuple.
        \ngeomsToColor---list of the name of geometries to color,default is 'all'
        """
        status = self.doitWrapper(name,seq,**kw)#apply( self.doitWrapper, (name, seq), kw)
        return status
        
commandList = [
    {'name':'buildDNA', 'cmd':BuildDNACommand(), 'gui':None}, 
    ]

def initModule(viewer):
    for dict in commandList:
        viewer.addCommand(dict['cmd'], dict['name'], dict['gui'])

        
#        
#payload = {'fiberform':'M1','submit':'Continue'}
#r = requests.post("http://w3dna.rutgers.edu/rebuild/fiberch", data=payload)
##parse the path <input type="hidden" name="path" value="data/usr/137_131_108_37/rebuild" />
#lines = r.text.split("\n")
#path=""
#for l in lines:
#    if l.find('name="path"') != -1 :
#        line =l.split()
#        for i,s in enumerate(line) :
#            if s=='name="path"' :
#                path = line[i+1].split("=")[1]
#                break
#        break
#
#payload = {'seq': 'ATGCCCGCC', 'dnaform':'M1','fiberform':'M1','submit':'Build',"path":path,"block":False}
#r = requests.post("http://w3dna.rutgers.edu/rebuild/progbar", data=payload)
#print r.text
#r = requests.post("http://w3dna.rutgers.edu/rebuild/regseq", data=payload)
##r = requests.post("http://w3dna.rutgers.edu/",data=payload)
##http://w3dna.rutgers.edu/data/usr/137_131_108_37/rebuild/
##http://w3dna.rutgers.edu/data/usr/137_131_108_37/rebuild/s0.pdb
##r = requests.get('http://w3dna.rutgers.edu/data/usr/137_131_108_37/rebuild/s0.pdb')
##import urllib
##urllib.urlretrieve ("http://w3dna.rutgers.edu/data/usr/137_131_108_37/rebuild/s0.pdb")
#
#done = False
#cut= 0
#while not done :
#    print cut
#    if cut > 100 :        
#        break
#    try :
#        dnafile = urllib2.urlopen("http://w3dna.rutgers.edu/data/usr/137_131_108_37/rebuild/s0.pdb")
#        done = True
#    except :
#        cut+=1        
#        continue
#if done :
#    output = open('s0.pdb','w')
#    output.write(dnafile.read())
#    output.close()

