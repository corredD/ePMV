# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 23:53:00 2012
###############################################################################
#
# autoPACK Authors: Graham T. Johnson, Ludovic Autin, Mostafa Al-Alusi, Michel Sanner
#   Based on COFFEE Script developed by Graham Johnson between 2005 and 2010
#   with assistance from Mostafa Al-Alusi in 2009 and periodic input
#   from Arthur Olson's Molecular Graphics Lab
#
# AFGui.py Authors: Ludovic Autin with minor editing/enhancement from Graham Johnson
#
# Copyright: Graham Johnson ©2010
#
# This file "upy_autoPack_plugin.py" is part of autoPACK, cellPACK, and AutoFill.
#
#    autoPACK is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    autoPACK is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with autoPACK (See "CopyingGNUGPL" in the installation.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
    
Name: 'AutoFill/AutoCell GUI'
@author: Ludovic Autin with minor editing/enhancement by Graham Johnson
"""

import bpy

#this should be part of the adaptor?
__author__ = "Ludovic Autin, Graham Johnson"
__url__ = [""]
__version__="0.0.0.1"
__doc__ = "AF v"+__version__
__doc__+"""\
AUTOFILL by Graham Jonhson,Ludovic Autin,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.
Develloped @UCSF.
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
#should be universal
bl_info = {
    "name": "cellPACK",
    "description": """by Ludovic Autin,Graham Jonhson,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.""",
    "author": "Ludovic Autin",
    "version": (0,0,3),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > cellPACK",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://autopack.org",
    "category": "Development"
}

import os,sys
#import platform

#SHOULD HANDLE SOME PYTHON SYSTEM PATH HERE
import bpy
import sys,os

bpath = bpy.app.binary_path
if sys.platform == "win32":
    os.chdir(os.path.dirname(bpath))
    #os.chdir("../")
    softdir = os.path.abspath(os.path.curdir)
    MGL_ROOT =softdir
    pyubicpath = softdir+"/MGLToolsPckgs"#"/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
    sys.path.insert(0,pyubicpath)
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
elif  sys.platform == "darwin":
    os.chdir(os.path.dirname(bpath))
    os.chdir("../../../")
    softdir = os.path.abspath(os.path.curdir)
    MGL_ROOT =softdir
    pyubicpath = softdir+"/MGLToolsPckgs"#"/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
    sys.path.insert(0,pyubicpath)
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
elif sys.platform  == "linux2" : #linux
    os.chdir(os.path.dirname(bpath))
    #os.chdir("../")
    softdir = os.path.abspath(os.path.curdir)
    MGL_ROOT =softdir
    pyubicpath = softdir+"/MGLToolsPckgs"#"/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
    sys.path.insert(0,pyubicpath)
    sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')
print (MGL_ROOT)
print (pyubicpath)

from time import time
	
#be sure to use a unique ID obtained from www.plugincafe.com
#from Blender import Draw
PLUGIN_ID = 5555551#need a plug id

#upy UIadaptor stuff
import upy
upy.setUIClass('blender25')

class AP_OT_launch(bpy.types.Operator):
    bl_idname = "ap.launch"
    bl_label = "cellPACK"
    
    def execute(self, context):
        #from AutoFill import AFGui
        from autopack import Gui
        afgui = Gui.AutoPackGui()
        afgui.setup(rep="af",host=upy.host)
        afgui.display()
        #create an empty object call "welcome to epmv ?"
        afobj = afgui.helper.newEmpty("Welcome to autoPack")
        return {'FINISHED'}
        
def menu_draw(self, context):
    self.layout.operator(AP_OT_launch.bl_idname)#,icon="PLUG")

classes = (
    AP_OT_launch,
    #EPMV_HT_icons
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_HT_header.append(menu_draw)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_draw) 
    bpy.types.VIEW3D_MT_object.append(menu_draw)
    bpy.types.VIEW3D_MT_editor_menus.append(menu_draw)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.INFO_HT_header.remove(menu_draw)
    #bpy.types.INFO_MT_add.remove(menu_draw)
    bpy.types.VIEW3D_MT_object.remove(menu_draw)
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_draw)

if __name__ == '__main__':
    register()

def test_cellPACK():
    import upy
    upy.setUIClass() #set the class
    from autopack import Gui
    afgui = Gui.AutoPackGui()
    afgui.setup(rep="af",host=upy.host)
    afgui.display()
    #create an empty object call "welcome to epmv ?"
    afobj = afgui.helper.newEmpty("Welcome to autoPack")