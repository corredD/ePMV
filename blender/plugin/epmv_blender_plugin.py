#!BPY

"""
Name: 'epmv'
Blender: 249b
Group: 'System'
Tooltip: 'Molecular Viewer'
"""

__url__ = ["http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Main_Page",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt',
           'http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Citation_Information',]
__version__="0.0.3a"
__bpydoc__ = "ePMV v"+__version__
__bpydoc__+="""\
Use Blender as a molecular viewer
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
#general import
import sys
import os
import re
import shutil
from time import time
import time as T
import Blender
global MGL_ROOT
MGL_ROOT="/Library/MGLTools/1.5.6.up"
def getMGL(filename):
        MGL_ROOT=filename
        print "whats upone",MGL_ROOT
        f=open(mgldirfile,'w')
        f.write(MGL_ROOT)
        f.close()
        
softdir = Blender.Get("homedir")
prefdir = Blender.Get('uscriptsdir')
if prefdir is None:
    prefdir = Blender.Get('scriptsdir')
mgldirfile=prefdir+os.sep+"mgltoolsdir"
personalize = False

if len(MGL_ROOT) == 0 :  
    if os.path.isfile(mgldirfile) :
        f=open(mgldirfile,'r')
        MGL_ROOT=f.readline()
        f.close()
    else :
        personalize = True
        if len(MGL_ROOT) == 0 :    
            MGL_ROOT=Blender.Draw.PupStrInput("what is the path to MGLToolsPckgs?:", "untitled", 100)
            if not os.path.exists(MGL_ROOT):
                if not os.path.exists(MGL_ROOT+os.sep+".."+os.sep+"MGLToolsPckgs"):
                    MGL_ROOT=Blender.Draw.PupStrInput("MGLToolsPckgs path:", "untitled", 100)
                else :
                    MGL_ROOT=MGL_ROOT+os.sep+".."+os.sep
        if os.path.exists(MGL_ROOT):
            f=open(mgldirfile,'w')
            f.write(MGL_ROOT)
            f.close()
    
if len(MGL_ROOT):
    if sys.platform == 'win32':
    #need to patch MGLTools first
    #first patch MGLTools
    #check if we need to patch
        mgltoolsDir = MGL_ROOT+os.sep+"MGLToolsPckgs"
        patch=os.path.isfile(mgltoolsDir+os.sep+"patched")
        if not patch :
            import urllib
            import tarfile 
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
#do I need to copy the file
    plugfile = prefdir+os.sep+"epmv_blender_plugin.py"
    print plugfile
    if not os.path.isfile(plugfile) :
        indir = MGL_ROOT+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+os.sep+\
            "blender"+os.sep+"plugin"+os.sep
        outdir = prefdir+os.sep
        print outdir
        files=[]
        files.append("epmv_blender_plugin.py")
        files.append("blenderPmvClientGUI.py") 
        files.append("epmv_blender_update.py")
        for f in files : 
            shutil.copy (indir+f, outdir+f)
        print "copy"
sys.path.append(MGL_ROOT+'/MGLToolsPckgs')
if sys.platform == "win32":
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
else :
    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages')
    sys.path.append(MGL_ROOT+'/lib/python2.5/site-packages/PIL')

from Blender import Draw

import pyubic
pyubic.setUIClass('blender')

from ePMV import epmvGui
epmvgui = epmvGui.epmvGui()
epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender')
#
#define the default options
epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                useLog = False,doCloud=False,forceFetch=False)

Draw.Register(epmvgui.CreateLayout, epmvgui.CoreMessage, epmvgui.Command)
