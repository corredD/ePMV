"""
Name: 'Python Molecular Viewer GUI'
Cinema4D: 12
Py4D:1.11
"""

#this should be part of the adaptor?
__author__ = "Ludovic Autin, Graham Johnson"
__url__ = ["http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Main_Page",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt']
__version__="0.0.2a"
__doc__ = "ePMV v"+__version__
__doc__+"""\
Use cinema4d as a molecular viewer

Provide gui interface to load and display Molecule Object (from pdb file for instance)
-load .pdb,.pdbqt,.pqr,.mol2,.cif
-display as CPK,Ball&Stick,Ribbon, MSMS and Coarse Molecular Surface
-color by: color,atom type, david goodsell atom type, resiude type, secondary structure type
-selection : any molecule levele MOL:CHAIN:RESIDUE:ATOM using keyword and picking functionality
-option available for : CPK, BS, CMS, MSMS under object selection...

ePMV by Ludovic Autin,Graham Jonhson,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.
"""
# -------------------------------------------------------------------------- 
# ***** BEGIN GPL LICENSE BLOCK ***** 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software Foundation, 
# Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK ***** 
# -------------------------------------------------------------------------- 
#=======
import os,sys
import c4d
MGL_ROOT="/Library/MGLTools/1.5.6.up"


prefpath=c4d.storage.GeGetC4DPath(1)
os.chdir(prefpath)
os.chdir(".."+os.sep)
softdir = os.path.abspath(os.curdir)
mgldirfile=softdir+os.sep+"plugins"+os.sep+"epmv"+os.sep+"mgltoolsdir"
if len(MGL_ROOT) == 0 :  
    if os.path.isfile(mgldirfile) :
        f=open(mgldirfile,'r')
        MGL_ROOT=f.readline()
        f.close()
    else :
        if len(MGL_ROOT) == 0 :
            MGL_ROOT = c4d.storage.LoadDialog(title="what is the path to MGLToolsPckgs?",flags=2)
        f=open(mgldirfile,'w')
        f.write(MGL_ROOT)
        f.close()
print MGL_ROOT
#is MGLTools Pacthed ie windows
if sys.platform == 'win32':
    #need to patch MGLTools first
    #first patch MGLTools
    #check if we need to patch
    mgltoolsDir = MGL_ROOT+os.sep+"MGLToolsPckgs"
    patch=os.path.isfile(mgltoolsDir+os.sep+"patched")
    if not patch :
        import urllib
        import tarfile 
        c4d.gui.MessageDialog("Patching MGLToolsPckgs with python2.6 system dependant modules")
        print mgltoolsDir+os.sep
        patchpath = mgltoolsDir+os.sep
        URI="http://mgldev.scripps.edu/projects/ePMV/patchs/depdtPckgs.tar"
        tmpFileName = mgltoolsDir+os.sep+"depdtPckgs.tar"
        if not os.path.isfile(tmpFileName):
            urllib.urlretrieve(URI, tmpFileName)
            #geturl(URI, tmpFileName)
        TF=tarfile.TarFile(tmpFileName)
        TF.extractall(patchpath)
        #create the pacthed file
        f=open(mgltoolsDir+os.sep+"patched","w")
        f.write("MGL patched!")
        f.close()
        c4d.gui.MessageDialog("MGLTools pacthed, click OK to continue")

#add to syspath
sys.path.append(MGL_ROOT+'/MGLToolsPckgs')
from Pmv.hostappInterface.install_plugin import Installer

epmvinstall = Installer(gui=False)

#is C4dpatched
if sys.platform == "darwin" :
	patchpath = c4d.storage.GeGetC4DPath(4)+os.sep+"python"+os.sep+"packages"+os.sep+"osx"+os.sep
elif sys.platform == "win32":
	patchpath = c4d.storage.GeGetC4DPath(2)+os.sep+"modules"+os.sep+"python"+os.sep+"res"+os.sep
epmvinstall.softdir[2] = softdir
print epmvinstall.softdir[2]
patched=os.path.isfile(patchpath+"patched")
if not patched :
    c4d.gui.MessageDialog("Cinema4D python library is going to be pacthed\n")
    epmvinstall.patchC4DR12(patchpath)
    c4d.gui.MessageDialog("Cinema4D python library have just beed patched you need to restart!\n")
    #c4d.CallCommand(12104)#quit

#check if we need to patch MGLTools / C4D
#TODO:
#make the pyrosetta extension
#loft did not work
#copy  libjpeg.62.dylib in /usr/lib ?
import c4d
from c4d import plugins
from c4d import utils
from c4d import bitmaps
from c4d import gui
#from c4d import symbols as sy

#setup the python Path
import sys
import os
from time import time
#if changePath :
#    sys.path.insert(1,sys.path[0]+"/lib-tk")
#    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages')
#    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages/PIL')

sys.path.append(MGL_ROOT+'/MGLToolsPckgs')
if sys.platform == "win32":
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
else :
    sys.path.insert(1,sys.path[0]+"/lib-tk")
    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages')
    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages/PIL')

#sys.path.append('/Library/MGLTools/REL/python2.6/lib/python2.6/site-packages')
#sys.path.append('/Library/Python/2.6/site-packages/')
#sys.path.append('/Library/Python/2.6/site-packages/numpy-1.3.0-py2.6-macosx-10.6-universal.egg/')
#sys.path.append('/Library/Python/2.6/site-packages/PIL/')

#sys.path.insert(0,"/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/")
#sys.path.insert(0,"/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-tk/")

#only need to do it once the sys path update....
    #pmv 1.6.0 seems to works perfect, no need to patch
    #even better if 64bits i guess

#be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1023406666
VERBOSE = 0

import pyubic
pyubic.setUIClass('c4d')

from ePMV import epmvGui

class epmv_C4dDialog(plugins.CommandData):
   """Class to register the entry in the plugins menu.
   In the most cases a dialog only needs to be in the
   memory when its really needed. So just allocate the memory
   for the dialog when the user calls it or CINEMA 4D restores
   it for the startup GUI."""
   dialog = None
   

   def Execute(self, doc):
         # create the dialog
         print "execute"   
         dname=doc.GetDocumentName()
         if self.dialog is None:
            self.dialog = epmvGui.epmvGui()
            self.dialog.setup(rep=dname,mglroot=MGL_ROOT,host='c4d')
            self.dialog.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                useLog = False,doCloud=False,forceFetch=False)
         return self.dialog.Open(PLUGIN_ID)
    
   def RestoreLayout(self, sec_ref):
         print "restore",sec_ref    
         doc=c4d.documents.GetActiveDocument()
         dname=doc.GetDocumentName()
         #print doc,dname,c4d.mv
         if self.dialog is None:
            self.dialog = epmvGui.epmvGui()
            self.dialog.setup(rep=dname,mglroot=MGL_ROOT,host='c4d')
            self.dialog.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                useLog = False,doCloud=False,forceFetch=False)
         self.dialog.restored=True
         return self.dialog.Restore(pluginid=PLUGIN_ID,secret=sec_ref)

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()
    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "pmv.tif")
    bmp.InitWith(fn)
    if not hasattr(c4d,'mv'):
        c4d.mv={}    
    plugins.RegisterCommandPlugin(id=PLUGIN_ID, str="ePMV",
                                     help="This is an embedded Molecular Viewer.",
                                     dat=epmv_C4dDialog(),info=0, icon=bmp)
