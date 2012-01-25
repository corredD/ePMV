#!BPY

"""
Name: 'ePMV'
Blender: 249b
Group: 'System'
Tooltip: 'Molecular Viewer'
"""

__url__ = ["http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Main_Page",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt',
           'http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Citation_Information',]
__version__="0.3.8"
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
import Blender
        
softdir = Blender.Get("homedir")
prefdir = Blender.Get('uscriptsdir')
if prefdir is None:
    prefdir = Blender.Get('scriptsdir')
mgldirfile=prefdir+os.sep+"mgltoolsdir"
personalize = False
if sys.platform == "win32":
    os.chdir(softdir)
    os.chdir("..")
elif  sys.platform == "darwin":
    os.chdir(os.path.dirname(softdir))
    os.chdir("../../../")
hostdir = os.path.abspath(os.path.curdir)
localpath=hostdir+os.sep+"MGLToolsPckgs"
local = False
print localpath
personalize = False
if os.path.exists(localpath):
    MGL_ROOT=hostdir
    local = True
elif os.path.isfile(mgldirfile) :
    f=open(mgldirfile,'r')
    MGL_ROOT=f.readline()
    f.close()
else :
    print ("ePMV is not correctly installed.\n try to resinstall\n"+mgldirfile)

#add to syspath
sys.path.append(MGL_ROOT+'/MGLToolsPckgs')
if not local :
    if sys.platform == "win32":
        sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
    else :
        sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages')
        sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages/PIL')
else :
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')

from Blender import Draw

import upy
upy.setUIClass('blender24')

from ePMV import epmvGui
epmvgui = epmvGui.epmvGui()
epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender24')
#
#define the default options
epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                useLog = False,doCloud=False,forceFetch=False)
epmvgui.epmv.doLight = True
Draw.Register(epmvgui.CreateLayout, epmvgui.CoreMessage, epmvgui.Command)
