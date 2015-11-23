
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/installer.py is part of ePMV.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
import os
import sys
import glob
import re
import time
try :
    import urllib.request as urllib# , urllib.parse, urllib.error
except :
    import urllib
import tarfile
import zipfile
import shutil
COPY="cp"
geturl=None
global OS
OS = os
#print __name__ #main
#print dir()

import ePMV
PATH = ePMV.__path__[0]
   
def _reporthook(numblocks, blocksize, filesize, url=None, pb = None):
    #print "reporthook(%s, %s, %s)" % (numblocks, blocksize, filesize)
    base = os.path.basename(url)
    #XXX Should handle possible filesize=-1.
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
    except:
        percent = 100
    if numblocks != 0:
        sys.stdout.write("\b"*70)
    sys.stdout.write("%-66s%3d%%" % (base, percent))
    if pb is not None:
        pb.set(percent)

def geturl(url, dst,pb=None):
    print("get url '%s' to '%s'" % (url, dst))
    doit = True
    try :
        doit = sys.stdout.isatty()
    except:
        doit = False
    if doit:
        urllib.urlretrieve(url, dst,
                           lambda nb, bs, fs, url=url: _reporthook(nb,bs,fs,url,pb))
        sys.stdout.write('\n')
    else:
       urllib.urlretrieve(url, dst)
       
#utility
#from mglutil.util import packageFilePath

#note : do we ask for Modeller, PyRosetta,etc...?
#seems yes, so should have a extension frames where user defeine path to extension
#as AR and AF are part of MGLToolsPckgs no need to check them
class Installer:
    def __init__(self, mgl=""):
        self.automaticSearch = False
        self.plateform = sys.platform
        self.rootDirectory="/"
        self.sharedDirectory=""
        self.userDirectory=""
        self.progDirectory=""
        self.SetDirectory()
        self.softdir={}#["","","",""]
        self.MODES = ["Blender","Cinema4D","Cinema4DR12","Maya"]
        self.extensions = ["modeller","pyrosetta","hollow","pymol"]
        self.extdir=[""]*len(self.extensions)#,"","",""]
        self.cb = [self.getBlenderDir,self.getC4dDir,self.getC4dr12Dir,self.getMayaDir]
        self.funcPatch = {"blender":None,"c4d":self.patchC4DR12,
        "maya":None}
        self.funcInstall={"blender":self.installBlender,"c4d":self.installC4dr12,
        "maya":self.installMaya}        
        self.msgInst={"blender":"""ePMV installed. 
Restart blender
The plugin should appear
in Scripts->System->ePMV
in the Scripts Window""",
        "c4d":"ePMV installed. Restart C4D, the plugin should appear under Python->Plugins->ePMV",
        "maya":"ePMV installed. Restart Maya, the plugin should appear in the Custom shelf"}
        self.v = []
        self.dir = []
        self.log = ""
        self.msg = None
        self.chooseDir=None
        self.curent =0
        self.choosenDir = None
        #if mgl is not None :
        self.setMGL(mgl=mgl)
        self.gui = None
        self.current_version = "0"
        self.PMVv=""
        self.upyv=""
        self.update_notes=""
        self.newPMV =""
        self.newePMV=""
        self.newupy=""

    def setMGL(self,mgl=""):
        self.MGL_ROOT = mgl
        self.ePMVDIR = mgl+ os.sep + "MGLToolsPckgs"+os.sep+"ePMV" 
        self.mgltoolsDir = self.MGL_ROOT+os.sep+"MGLToolsPckgs"
        self.currDir = self.ePMVDIR

    def linuxwhich(self,program):
        #this function is also in mglutil.util.packageFilePath.py
        import os
        def is_exe(fpath):
            return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
    
        return None

    def SetDirectory(self):
        #according OS will set all the basic directory:
        #user/progam/root
        #in Win XP/2k/2k3 it is C:\Documents and Settings\%username%\
        #in Vista, it is C:\Users\%username%\
        #%HOMEPATH%.+
        self.userDirectory=os.getenv("HOME")
        if self.plateform == 'darwin':
            COPY="cp -r"
            #self.progDirectory="/Applications/" #Mac
            #self.preferencesDir=self.userDirectory+"/Library/Preferences/"
            self.sharedDirectory="/Users/Shared/"
        elif self.plateform == 'linux':
            COPY="cp -r"
            #self.progDirectory=os.environ["PATH"].split(os.pathsep)
            #self.preferencesDir=self.userDirectory
            self.sharedDirectory="/home/"
        elif self.plateform == 'win32':
            COPY="xcopy"
            #self.userDirectory="C:"+os.getenv("HOMEPATH")
            #self.progDirectory="C:"+os.sep+"Program Files"+os.sep
            self.preferencesDir=os.getenv("APPDATA")

                    
    def install(self):
        f=open(self.mgltoolsDir+os.sep+'MGLToolsPckgs'+os.sep+'Pmv'+os.sep+'hostappInterface'+os.sep+'epmv_dir.txt','a')
        for i,v in enumerate(self.v):
            val=v.get()
            if val : 
                print("install epmv plug for ",self.MODES[i])
                self.log+="\ninstall epmv plug for "+self.MODES[i]
                self.msg.set(self.log)                
                self.funcInstall[i]()
                #store directory
                f.write(self.MODES[i]+":"+self.softdir[i]+"\n")
        f.close()
        self.makeExtensionfile()
        self.log+="\nSUCCESS YOU CAN QUIT !"
        print(self.log)
        self.msg.set(self.log)

    def DirCallback(self,widget, event=None):
        values =  widget.get()
        print(values)
        
    def quitDir(self):
        dir = self.choosenDir.get()
        print("quitDir",dir)
        if self.plateform == "darwin":
            dir = dir.replace(" ","\ ")
        self.dir[self.curent].set(dir)
        self.softdir[self.curent] = dir    
        self.chooseDir.destroy()

    def getDirFromFile(self):
        #we get the soft dir from a file in Pmv/hostappinterface/epmv_dir.txt
        f=open(self.currDir+os.sep+'epmv_dir.txt','r')
        lines=f.readlines()
        f.close()
        #now parse it ie format : soft/extension dir
        for line in lines :
            elem = line.split(":")
            for i,soft in enumerate(self.MODES):
                if elem[0].lower() == self.MODES[i].lower():
                    self.softdir[i]=elem[1].strip()

    def getBlenderDir(self):
        if self.plateform.find("linux") != -1:
            dir=self.findDirectoryFrom(".blender",self.userDirectory+"/",sp=".*")
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.userDirectory, title="where is blender script directory, ie .blender/script")
                dir = x#self.softdir[2]
            else :
                dir = dir[0]
            dir = dir.replace(" ","\ ")
            self.dir[0].set(dir)
            self.softdir[0] = dir
        elif self.plateform == 'darwin':
            dir=self.findDirectoryFrom("blender",self.progDirectory+"/")
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.userDirectory, title="where is blender script directory, ie .blender/script")
                dir = x#self.softdir[2]
                self.dir[0].set(dir)
                self.softdir[0] = dir
            elif len(dir) == 1 :
                dir = dir[0]
                dir = dir.replace(" ","\ ")
                self.dir[0].set(dir)
                self.softdir[0] = dir
            else :
                self.chooseDirectory(0,dir)
        elif self.plateform == 'win32':
            #blender can be in Prgoram files or Application Data
            #dir=self.findDirectoryFrom("Blender Foundation",self.progDirectory)
            #if len(dir) == 0 :
            dir=self.findDirectoryFrom("Blender Foundation",self.preferencesDir)
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.userDirectory, title="where is the Blender Foundation directory")
                dir = x
                self.dir[0].set(dir)
                self.softdir[0] = dir     
            elif len(dir) == 1 :
                dir = dir[0]
#                dir = dir+os.sep+"Blender"+os.sep+".blender"+os.sep
                self.dir[0].set(dir)
                self.softdir[0] = dir
            else :
                self.chooseDirectory(0,dir)
        if self.automaticSearch :
            t1=time.time()
            self.progressbar.setLabelText('searching '+".blender")
            #is blender define in path
            dir=""#packageFilePath.which('blender')
            if dir == None :
                dir=self.findDirectory(".blender",self.progDirectory)
                if dir is None :
                    dir=self.findDirectory(".blender",self.userDirectory)
                    if dir is None :
                    #dir=self.findDirectory(".blender",self.rootDirectory)
                    #if dir is None:
                        dir="not Found"
                        return 
            print("time to find", time.time()-t1)
            print(dir)
            dir = dir.replace(" ","\ ")
            self.dir[0].set(dir)
            self.softdir[0] = dir
        
    def getC4dDir(self):
        dir = None
        if self.plateform == "darwin":
            dir=self.findDirectoryFrom("CINEMA 4D R11.5",self.progDirectory+"/MAXON/")
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.progDirectory, title="where is CINEMA4D 4D R11.5 plugin directory")
                dir = x
                self.dir[1].set(dir)
                self.softdir[1] = dir                
            elif len(dir) == 1 :
                dir = dir.replace(" ","\ ")
                self.dir[1].set(dir)
                self.softdir[1] = dir
            else :
                self.chooseDirectory(1,dir)
#                dir = dir[0]
        if self.automaticSearch :
            t1=time.time()
            self.progressbar.setLabelText('searching '+"Py4D")
            dir=self.findDirectory("Py4D",self.progDirectory)
            #if dir is None :
            #    dir=self.findDirectory("Py4D",self.progDirectory)
            if dir is None:
                    dir="not Found"
                    return
            print("time to find", time.time()-t1)
            dir = dir.replace(" ","\ ")
            self.dir[1].set(dir)
            self.softdir[1] = dir

    def getC4dr12Dir(self):
        dir = None
        if self.plateform == "darwin":
            dir=self.findDirectoryFrom("CINEMA 4D R12",self.preferencesDir+"/MAXON/")
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.preferencesDir, title="where is CINEMA4D 4D R12 user preferences directory")
                dir = x
                self.dir[2].set(dir)
                self.softdir[2] = dir
            elif len(dir) == 1 :
                dir = dir[0]
                dir = dir.replace(" ","\ ")
                self.dir[2].set(dir)
                self.softdir[2] = dir
            else :
                self.chooseDirectory(2,dir)
        elif self.plateform == "win32":
            dir=self.findDirectoryFrom("CINEMA 4D R12",self.preferencesDir+os.sep+"MAXON"+os.sep)
            if len(dir) == 0 :
                x = askdirectory(initialdir=self.preferencesDir, title="where is CINEMA4D 4D R12 user preferences directory")
                dir = x
                self.dir[2].set(dir)
                self.softdir[2] = dir                
            elif len(dir) == 1 :
                dir = dir[0]
#            dir = dir + "/plugins/Py4D/"
                self.dir[2].set(dir)
                self.softdir[2] = dir
            else :
                self.chooseDirectory(2,dir)
        if self.automaticSearch and dir is None :
            t1=time.time()
            self.progressbar.setLabelText('searching '+"C4D R12")
            dir=self.findDirectory("CINEMA 4D R12",self.progDirectory)
            #if dir is None :
            #    dir=self.findDirectory("Py4D",self.progDirectory)
            if dir is None:
                    dir="not Found"
                    return
            print("time to find", time.time()-t1)
            dir = dir.replace(" ","\ ")
            self.dir[2].set(dir)
            self.softdir[2] = dir
        
    def getMayaDir(self):
        #if self.plateform == "darwin":
        dir=self.sharedDirectory+"/Autodesk/maya/2011/plug-ins/"
        if not os.path.exists(dir):
            x = self.gui.fileDialog(label="where is MAYA2011 plugin directory")
            dir = x                
        #self.dir[3].set(dir)
        self.softdir["maya"][1] = dir
    
    def patchPMV(self,):
        patch=os.path.isfile(self.mgltoolsDir+os.sep+"patched")
        if not patch :
            #import urllib.request, urllib.parse, urllib.error
            import tarfile 
            print(self.mgltoolsDir+os.sep)
            patchpath = self.mgltoolsDir+os.sep
            URI="http://mgldev.scripps.edu/projects/ePMV/patchs/depdtPckgs.tar"
            tmpFileName = self.mgltoolsDir+os.sep+"depdtPckgs.tar"
            if not os.path.isfile(tmpFileName):
                urllib.urlretrieve(URI, tmpFileName)
                #geturl(URI, tmpFileName)
            TF=tarfile.TarFile(tmpFileName)
            TF.extractall(patchpath)
            #create the pacthed file
            f=open(self.mgltoolsDir+os.sep+"patched","w")
            f.write("MGL patched!")
            f.close()

    def patchPMV_64(self,):
        patch=os.path.isfile(self.mgltoolsDir+os.sep+"patched")
        if not patch :
            #import urllib.request, urllib.parse, urllib.error
            import tarfile
            print(self.mgltoolsDir+os.sep)
            patchpath = self.mgltoolsDir+os.sep
            URI="http://mgldev.scripps.edu/projects/ePMV/patchs/depdtPckgs_64.tar"
            tmpFileName = self.mgltoolsDir+os.sep+"depdtPckgs.tar"
            if not os.path.isfile(tmpFileName):
                urllib.urlretrieve(URI, tmpFileName)
                #geturl(URI, tmpFileName)
            TF=tarfile.TarFile(tmpFileName)
            TF.extractall(patchpath)
            #create the pacthed file
            f=open(self.mgltoolsDir+os.sep+"patched","w")
            f.write("MGL patched!")
            f.close()

    def installBlender(self):
        indir = self.ePMVDIR+os.sep+"blender"+os.sep+"plugin"+os.sep
        plugfile = self.softdir["blender"][0]+os.sep+"epmv_blender_plugin.py"
        print(plugfile)
        if not os.path.isfile(plugfile) :
            indir = self.MGL_ROOT+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+os.sep+\
                "blender"+os.sep+"plugin"+os.sep
            outdir = self.softdir["blender"][0]+os.sep
            print(outdir)
            files=[]
            files.append("epmv_blender_plugin.py")
            files.append("blenderPmvClientGUI.py") 
            files.append("epmv_blender_update.py")
            for f in files : 
                shutil.copy (indir+f, outdir+f)
            print("copy")
        #no need to patch linux and mac as there is blender python2.5
        #What about windows, already patch MGL but do we need to patch blender?
        
    def installC4d(self,update=False):
        self.log+="\ninstall c4d-epmv plug in "+self.softdir[1]+os.sep+"plugins/Py4D"
        self.msg.set(self.log)
        dir = self.softdir[1] 
        if self.plateform == "darwin":
            dir = dir.replace("\ "," ")
        py4ddir=dir+os.sep+"plugins/Py4D"
        #copy the directory of plugin to c4d/plugins/Py4D/plugins/.
        #Py4D should be already patched
        if not update:
            if not os.path.exists(py4ddir):
                patchpath = dir
                self.progressbar.setLabelText("getting  Py4D")
                URI="http://mgldev.scripps.edu/projects/ePMV/py4d.tar" #or Tku.tar
                tmpFileName = dir+"/py4d.tar"
                geturl(URI, tmpFileName,pb=self.progressbar)
                TF=tarfile.TarFile(tmpFileName)
                TF.extractall(patchpath)
            dirname1=self.currDir+os.sep+"cinema4d"+os.sep+"plugin"
            dirname2=py4ddir+os.sep+"plugins"+os.sep+"epmv"
            if os.path.exists(dirname2):
                shutil.rmtree(dirname2,True)
            shutil.copytree (dirname1, dirname2)            
            #copy the color per vertex c++ plugin
            filename1=py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv_c4d_plugin.py"
            filename2=py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv.pyp"
            shutil.copy (filename1, filename2)
            filename1=py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv_update.py"
            filename2=py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv_synchro.pyp"
            shutil.copy (filename1, filename2)
            filename1=self.currDir+os.sep+"cinema4d"+os.sep+"VertexColor.dylib"
            filename2=dir+os.sep+"plugins/VertexColor.dylib"
            shutil.copy (filename1, filename2)
        else :
            cmd="cp "+self.currDir+os.sep+"cinema4d"+os.sep+"plugin"+os.sep+"*.py "+self.softdir[1]+os.sep+"plugins"+os.sep+"epmv"+os.sep+"."
            print(cmd)
            os.system(cmd)
        #update the header changing the MGLTOOLS value
        files=[]
        files.append(py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv_c4d_plugin.py")
        files.append(py4ddir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"epmv.pyp")
        for f in files : 
            self.changeHeaderFile(f)

    def patchC4DR12(self):
        if self.plateform == "darwin" :
        	patchpath = self.softdir["c4d"][1]+os.sep+"python"+os.sep+"packages"+os.sep+"osx"+os.sep
        elif self.plateform == "win32":
        	patchpath = self.softdir["c4d"][1]+os.sep+"modules"+os.sep+"python"+os.sep+"res"+os.sep
        patched=os.path.isfile(patchpath+"patched")
        if not patched :
            dir = self.softdir["c4d"][0]
            if self.plateform == "darwin":
                URI="http://mgldev.scripps.edu/projects/ePMV/Tk.tar" #or Tku.tar
                tmpFileName = dir+"/library/python/packages/osx/Tk.tar"
                geturl(URI, tmpFileName)
                TF=tarfile.TarFile(tmpFileName)
                TF.extractall(patchpath)
                f=open(patchpath+"patched","w")
                f.write("C4D patched!")
                f.close()                    
            elif self.plateform == "win32":
                name1="Python.win32.framework"
                name2="Python.win32.framework.original"
                print(patchpath+name1)
                if not os.path.exists(patchpath+name2):
                    os.rename(patchpath+name1,patchpath+name2)
                #we simply Copy the C:\\Python26 directory....
                dirname1="C:\\Python26\\"
                dirname2=patchpath+name1
                shutil.copytree (dirname1, dirname2)         
                
#                URI="http://mgldev.scripps.edu/projects/ePMV/patchs/py26win.tar"
#                tmpFileName = patchpath+"py26win.tar"
                #self.progressbar.setLabelText("patching C4D python")
#                if not os.path.isfile(tmpFileName):
#                    geturl(URI, tmpFileName)
#                TF=tarfile.TarFile(tmpFileName)
#                if not os.path.exists(patchpath+name2):
#                    os.rename(patchpath+name1,patchpath+name2)
#                TF.extractall(patchpath)
                f=open(patchpath+"patched","w")
                f.write("C4D patched!")
                f.close()        

    def installC4dr12(self):
        dir = self.softdir["c4d"][0]
#        if self.plateform == "darwin":
#           dir = dir.replace("\ "," ")
        print("install c4dr12-epmv plug in ",self.softdir["c4d"][0])     
        import shutil
        dirname1=self.ePMVDIR+os.sep+"cinema4d"+os.sep+"plugin"
        dirname2=dir+os.sep+"plugins"+os.sep+"ePMV"
        print(dirname1,dirname2)
        if os.path.exists(dirname2):
            shutil.rmtree(dirname2,True)
        shutil.copytree (dirname1, dirname2)
        
    def personalizeMaya(self,plugdir,prefDir):
        shelfMel="""
shelfButton
        -enableCommandRepeat 1
        -enable 1
        -width 35
        -height 35
        -manage 1
        -visible 1
        -preventOverride 0
        -annotation "import maya\\nmaya.cmds.ePMV()\\nepmv = maya.mv['epmv']\\nself = epmv.mv\\n" 
        -enableBackground 0
        -align "center" 
        -label "ePMV" 
        -labelOffset 0
        -font "plainLabelFont" 
        -imageOverlayLabel "ePMV" 
        -overlayLabelColor 0.8 0.8 0.8 
        -overlayLabelBackColor 0 0 0 0.2
"""
        logo = plugdir+os.sep+"images"+os.sep+"pmv.tif"
        shelfMel+='        -image "%s"\n' % (logo.replace("\\","/"))
        shelfMel+='        -image1 "%s"\n' % (logo.replace("\\","/"))
        shelfMel+="""
        -style "iconOnly" 
        -marginWidth 1
        -marginHeight 1
        -command "import maya\\nmaya.cmds.ePMV()\\nepmv = maya.mv['epmv']\\nself = epmv.mv\\n"
        -sourceType "python" 
        -commandRepeatable 1
    ;
"""
        windowsPref = "windowPref -topLeftCorner 413 640 -widthHeight 960 480 ePMV;"
        pluginPref = 'evalDeferred("autoLoadPlugin(\"\", \"ePMV.py\", \"ePMV\")");'
        
        filename = prefDir+os.sep+"shelves"+os.sep+"shelf_Custom.mel"
        #test if exist if not create.
        if os.path.isfile(filename):
            f=open(filename,'r')
            lines = f.readlines()
            f.close()
        else :
            f=open(filename,'w')
            lines="""global proc shelf_Custom () {
global string $gBuffStr;
global string $gBuffStr0;
global string $gBuffStr1;
}"""
            f.write(lines)
            f.close()
        f=open(prefDir+os.sep+"shelves"+os.sep+"shelf_Custom.mel",'w')
        lines = lines[:-1]
        for line in lines:
            f.write(line)
        f.write(shelfMel)
        f.write("}\n")
        f.close()
        #change the plugin preferences too
        f=open(prefDir+os.sep+"pluginPrefs.mel",'a')
        f.write('evalDeferred("autoLoadPlugin(\\"\\", \\"ePMV.py\\", \\"ePMV\\")");')
        f.close()
        
        
    def installMaya(self,update=False):
        #now how to make it available!
        #what about windows
        #maya is in /Applications/Autodesk/maya2011/Maya.app/Contents/MacOS/plug-ins/ePMV.py
        #preferences are in /Users/ludo/Library/Preferences/Autodesk/maya/2011/prefs
        #and on windowsXP : C:\Documents and Settings\ludo\My Documents\maya\2011\prefs
        #and on windows7 vista : C:\Users\USERNAME\Documents\maya\2011\
        #self.getMayaDir()
        self.personalizeMaya(self.ePMVDIR,self.softdir["maya"][0])
        #copy epmv_may_plugin.py in plugin dir
        #1 link the plugin to plug-dir or copy? plugin is in maya.app folder
        #special case of /Users/shared/maya/plugin
#        cmd="cp "+self.currDir+"/autodeskmaya/plugin/mayaPMVui.py "+self.softdir[3]+"/ePMV.py"
        file1=self.ePMVDIR+os.sep+"autodeskmaya"+os.sep+"plugin"+os.sep+"epmv_maya_plugin.py"
        #need to be in plugin dir...not script...next to mMaya?
        if not os.path.exists(self.softdir["maya"][1]):
            os.mkdir(self.softdir["maya"][1])
            print(self.softdir["maya"][1]+" created")
        file2 = self.softdir["maya"][1]+os.sep+"epmv_maya_plugin.py"
        try :
            shutil.copy (file1, file2)
        except IOError :
            print("Unable to copy file. %s" % file1)


    def changeHeaderFile(self,file):
        if self.plateform != "win32":
            file=file.replace('\\','')
            self.mgltoolsDir = self.mgltoolsDir.replace("\n","\\n")
        data = open(file,'r').read()
        o = open(file,"w")
        o.write( re.sub('MGL_ROOT=""','MGL_ROOT="'+self.mgltoolsDir+'"',data) )
        o.close()       

    def checkForUpdate(self,*args):
        #check on web if update available
        #return boolean for update_PMV,update_ePMV and update_pyubics
        upPMV=False
        upePMV=False
        upupy=False
        self.newPMV =""
        self.newePMV=""
        self.newupy=""
        self.update_notes = ""
        #need version
        URI="http://mgldev.scripps.edu/projects/ePMV/update_notes.txt"
        tmpFileName = self.mgltoolsDir+os.sep+"update_notes.txt"
#        if not os.path.isfile(tmpFileName):
        urllib.urlretrieve(URI, tmpFileName)
            #geturl(URI, tmpFileName)
        f= open(tmpFileName,"r")
        lines = f.readlines()
        f.close()
        #get the version
        n=len(lines)
        for i,l in enumerate(lines) :
            s=l.strip().split(":")
            print(s,self.PMVv,self.current_version,self.upyv)
            if s[0] == "PMV":
                self.newPMV=s[1]
                if s[1] != self.PMVv:
                    print(s[1],self.PMVv)
                    #upPMV = True
            if s[0] == "ePMV":
                self.newePMV=s[1]
                if s[1] != self.current_version:
                    print(s[1],self.current_version)
                    upePMV = True
            if s[0] == "upy":
                self.newupy=s[1]
                if s[1] != self.upyv:
                    print(s[1],self.upyv)
                    upupy = True
            if s[0] == "Notes":
#                self.update_notes = lines[i:]
#                break
                for j in range(i+1,n):
                    #print j,lines[j]
                    self.update_notes+=lines[j]
                break
            print(self.update_notes)
        os.remove(tmpFileName)
        return upPMV,upePMV,upupy

    def update_PMV(self,backup=False):
        #get the new epmv folder
        #do we do a backup
        patchpath = self.MGL_ROOT+os.sep
        URI="http://mgldev.scripps.edu/projects/ePMV/updates/pmv.tar"
        tmpFileName = self.MGL_ROOT+os.sep+"pmv.tar"
        if not os.path.isfile(tmpFileName):
            urllib.urlretrieve(URI, tmpFileName)
            #geturl(URI, tmpFileName)
        TF=tarfile.TarFile(tmpFileName)
        dirname1=self.mgltoolsDir
        import shutil        
        if backup :
            #rename ePMV to ePMVv
            dirname2=self.mgltoolsDir+self.PMVv
            print(dirname1,dirname2)
            if os.path.exists(dirname2):
                shutil.rmtree(dirname2,True)
            shutil.copytree (dirname1, dirname2)
        if os.path.exists(dirname1):
            shutil.rmtree(dirname1,True)
        TF.extractall(patchpath)
        os.remove(tmpFileName)
        
    def update_ePMV(self,backup=False):
        #get the new epmv folder
        #do we do a backup
        import ePMV
        patchpath = self.mgltoolsDir+os.sep
        URI="http://mgldev.scripps.edu/projects/ePMV/updates/epmv.zip"
        tmpFileName = self.mgltoolsDir+os.sep+"epmv.zip"
#        if not os.path.isfile(tmpFileName):
        urllib.urlretrieve(URI, tmpFileName)
            #geturl(URI, tmpFileName)
        zfile = zipfile.ZipFile(tmpFileName)
        #TF=tarfile.TarFile(tmpFileName)
        dirname1=self.ePMVDIR
        import shutil        
        if backup :
            #rename ePMV to ePMVv
            dirname2=self.ePMVDIR+ePMV.__version__
            print(dirname1,dirname2)
            if os.path.exists(dirname2):
                shutil.rmtree(dirname2,True)
            shutil.copytree (dirname1, dirname2)
        if os.path.exists(dirname1):
            shutil.rmtree(dirname1,True)           
        zfile.extractall(patchpath)
#        os.remove(tmpFileName)
        
    def update_upy(self,backup=False):
        import upy
        patchpath = self.mgltoolsDir+os.sep
        URI="http://mgldev.scripps.edu/projects/ePMV/updates/upy.zip"
        tmpFileName = self.mgltoolsDir+os.sep+"upy.zip"
#        if not os.path.isfile(tmpFileName):
        urllib.urlretrieve(URI, tmpFileName)
            #geturl(URI, tmpFileName)
#        TF=tarfile.TarFile(tmpFileName)
        zfile = zipfile.ZipFile(tmpFileName)

        dirname1=self.mgltoolsDir+os.sep+"upy"
        import shutil        
        if backup :
            #rename ePMV to ePMVv
            dirname2=dirname1+upy.__version__
            print(dirname1,dirname2)
            if os.path.exists(dirname2):
                shutil.rmtree(dirname2,True)
            shutil.copytree (dirname1, dirname2)
        if os.path.exists(dirname1):
            shutil.rmtree(dirname1,True)           
        zfile.extractall(patchpath)
#        os.remove(tmpFileName)

    def update(self,pmv=False,epmv=False,upy=False,backup=False):
#        if pmv : 
#           self.update_PMV(backup=backup)
        if epmv :
            self.update_ePMV(backup=backup)
        if upy:
            self.update_upy(backup=backup)
            
    def updateCVS(self,full=False):
        if full:
            cmd="cd "+self.mgltoolsDir+"\n"
        else :
            cmd="cd "+self.currDir+"\n"
        cmd+="cvs -d:pserver:anonymous@mgl1.scripps.edu:/opt/cvs update\n"
        os.system(cmd)

    def addExtensionToFile(self,string):
        f=open(PATH+os.sep+'extension'+os.sep+'liste.txt','a')
        f.write(string+"\n")
        f.close()

    def addExtension(self,string):
        self.getExtensionDirFromFile()
        elem = string.split(":")
        print(elem)
        for i,soft in enumerate(self.extensions):
                if elem[0].lower() == self.extensions[i].lower():
                    if self.extdir[i] is "":
                        self.extdir[i]=elem[1].strip()
                        self.addExtensionToFile(string)

    def makeExtensionfile(self):
        f=open(self.currDir+os.sep+'extension'+os.sep+'liste.txt','w')
        f.write("#put your extension name and directory here\n")
        f.close()

    def getExtensionDirFromFile(self):
        #we get the soft dir from a file in Pmv/hostappinterface/epmv_dir.txt
        fname=PATH+os.sep+'extension'+os.sep+'liste.txt'
        if not os.path.isfile(fname):
            f=open(fname,'w')
            f.write("#extension dir\n")
            f.close()
        f=open(fname,'r')
        lines=f.readlines()
        f.close()
        #now parse it ie format : soft/extension dir
        for line in lines :
            elem = line.split(":")
            for i,soft in enumerate(self.extensions):
                if elem[0].lower() == self.extensions[i].lower():
                    self.extdir[i]=elem[1].strip()

import upy
upy.setUIClass()
from upy import uiadaptor
helperClass = upy.getHelperClass()

class InstGui(uiadaptor):
    def setup(self,inst=None,mgl=None,**kw):
        import os
        #uiadaptor.__init__(self,kw)
#        self.y = 200 #top line
        #self.title = "Install ePMV"
        self.inst = inst
        if inst is not None:
            self.inst.gui = self
        self.MGL_ROOT = mgl
        self.platform = self.inst.plateform
        self.getDirectory()
        self.inst.softdir[self.host] = [self.prefdir,self.softdir]
        self.mgldirfile = self.prefdir+os.sep+"mgltoolsdir"
        self.initWidget(id=10)
        self.setupLayout()
        
    #theses two function are for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1

    def Command(self,*args):
#        print args
        self._command(args)
        self.updateViewer()
        return 1

    def initWidget(self,id=None):
        self.SELEDIT_TEXT = self._addElemt(name="MGLTools path",action=self.getMGL,width=100,
                          value=self.MGL_ROOT,type="inputStr",variable=self.addVariable("str",self.MGL_ROOT))
        self.LOAD_BTN = self._addElemt(name="...",width=20,height=10,
                         action=self.browseMGLTools,type="button")
        self.DOIT_BTN = self._addElemt(name="install",width=40,height=10,
                         action=self.installePMV,type="button")
        self.CANCEL = self._addElemt(name="cancel",width=40,height=10,
                         action=self.close,type="button")
#        self.LOG = 
    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        self._layout = []
        self._layout.append([self.SELEDIT_TEXT,self.LOAD_BTN])
        self._layout.append([self.DOIT_BTN,self.CANCEL])

    def getMGL(self,*args):
        print("args", args)
        filename = args[0]
        self.MGL_ROOT=filename
        print("whats upone",self.MGL_ROOT)
        f=open(self.mgldirfile,'w')
        f.write(self.MGL_ROOT)
        f.close()
        self.setVal(self.SELEDIT_TEXT,self.MGL_ROOT)

    def browseMGLTools(self,*args):
        file = self.fileDialog(label="choose a file")
        print("browse",file)
        self.getMGL(file)
                
    def installePMV(self,*args):
        print(args)
        print("dir",dir())
        print("MGL",self.MGL_ROOT)
        self.getMGL(self.MGL_ROOT)
        if self.platform == 'win32':
            self.drawMessage(title="Patch required",message="PMV is going to be patch for windows python2.6 compatibility.")
            self.inst.patchPMV()
            self.drawMessage(title="Patch Done",message="PMV pacthed, click OK to continue")
        if self.inst.funcPatch[self.host] is not None : 
            self.drawMessage(title=self.host+" pacth",message=self.host+" is going to be patched")
            self.inst.funcPatch[self.host]()
            self.drawMessage(title=self.host+" pacthed",message="click OK to continue")
        self.inst.funcInstall[self.host]()
        #self.inst.patchC4DR12()
        msg = self.inst.msgInst[self.host]+"\n"
        msg+= self.prefdir+"\n"
        msg+= self.softdir+"\n"
        self.drawMessage(title="ePMV installed",message=msg)
        self.close()
