
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/blender/v24/plugin/epmv_blender_plugin.py is part of ePMV.

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

#from Blender import Draw

from ePMV import epmvGui
#epmvgui = epmvGui.epmvGui()
#epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender24')
##
##define the default options
#epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
#                useLog = False,doCloud=False,forceFetch=False)
#epmvgui.epmv.doLight = True
#Draw.Register(epmvgui.CreateLayout, epmvgui.CoreMessage, epmvgui.Command)

#be sure to use a unique ID obtained from www.plugincafe.com
#from Blender import Draw
PLUGIN_ID = 1027431
import upy
upy.setUIClass()

plugTypeClass,opType = upy.getPluginClass(plug="command")#= operator in blender

from ePMV import epmvGui

print ((plugTypeClass))

class epmv_Dialog(plugTypeClass):
    def setgui(self,dname):
        self.gui = epmvGui.epmvGui()
        self.gui.setup(rep="epmv",mglroot=MGL_ROOT,host=upy.host)
        self.gui.epmv.Set(bicyl=True,use_progressBar = False,doLight = False,doCamera = False,
        useLog = False,forceFetch=False)
        self.hasGui = True
        self.gui.display()
        
    def resetgui(self,dname):
        self.gui = epmvGui.epmvGui()
        self.gui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender25')
        self.gui.epmv.Set(bicyl=True,use_progressBar = False,doLight = False,doCamera = False,
                useLog = False,forceFetch=False)
        self.gui.display()
        
epmv_plugin = epmv_Dialog(name="ePMV",pluginId=PLUGIN_ID,
                              tooltip="This is an embedded Molecular Viewer",
                              hasGui=True)

epmv_plugin.setIcon(image_name="pmv.tif")

if "__res__" in locals() :
    epmv_plugin.register(epmv_Dialog,Object=epmv_plugin,menuadd={"head":None,"mt":None},res=__res__)
else :
    epmv_plugin.register(epmv_Dialog,Object=epmv_plugin,menuadd={"head":None,"mt":None})

def register():
    print (__name__)
def unregister():
    pass