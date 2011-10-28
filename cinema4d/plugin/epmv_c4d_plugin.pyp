"""
Name: 'Python Molecular Viewer GUI'
Cinema4D: 12
"""

#this should be part of the adaptor?
__author__ = "Ludovic Autin, Graham Johnson"
__url__ = ["http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Main_Page",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt']
__version__="0.4.0"
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

prefpath=c4d.storage.GeGetC4DPath(1)
os.chdir(prefpath)
os.chdir(".."+os.sep)
softdir = os.path.abspath(os.curdir)
MGL_ROOT=""
mgldirfile=softdir+os.sep+"mgltoolsdir"
local = False
localpath = softdir+os.sep+"plugins"+os.sep+"ePMV"+os.sep+"MGLToolsPckgs"
print localpath
if os.path.exists(localpath):
        MGL_ROOT=softdir+os.sep+"ePMV"+os.sep
        local = True
elif os.path.isfile(mgldirfile) :
        f=open(mgldirfile,'r')
        MGL_ROOT=f.readline()
        f.close()
else :
	    msg = "ePMV is not correctly installed.\n try to resinstall\n"+mgldirfile+"\n"+localpath
	    c4d.gui.MessageDialog(msg)
        #exit()
#add to syspath
sys.path.append(MGL_ROOT+'/MGLToolsPckgs')

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
if not local :
    if sys.platform == "win32":
        sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
    else :
        sys.path.insert(1,sys.path[0]+"/lib-tk")
        sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages')
        sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages/PIL')
else :
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
    sys.path.insert(1,MGL_ROOT+'/MGLToolsPckgs/lib-tk')
	
#be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1027431
VERBOSE = 0

import upy
upy.setUIClass('c4d')

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
            self.dialog.epmv.Set(bicyl=True,use_progressBar = False,doLight = False,doCamera = False,
                useLog = False,forceFetch=False)
         return self.dialog.Open(PLUGIN_ID,defaultw=400, defaulth=550)
    
   def RestoreLayout(self, sec_ref):
         print "restore",sec_ref    
         doc=c4d.documents.GetActiveDocument()
         dname=doc.GetDocumentName()
         #print doc,dname,c4d.mv
         if self.dialog is None:
            self.dialog = epmvGui.epmvGui()
            self.dialog.setup(rep=dname,mglroot=MGL_ROOT,host='c4d')
            self.dialog.epmv.Set(bicyl=True,use_progressBar = False,doLight = False,doCamera = False,
                useLog = False,forceFetch=False)
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
