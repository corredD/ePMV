# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "ePMV",
    "description": """Use Blender as a molecular viewer
ePMV by Ludovic Autin,Graham Jonhson,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.""",
    "author": "Ludovic Autin",
    "version": (0, 7, 6),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > ePMV",
    "wiki_url": "http://epmv.scripps.edu/",
    "category": "Development"
}

#general import
__url__ = ["http://epmv.scripps.edu/",
           'http://epmv.scripps.edu/citationinformation',]

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

import upy
upy.setUIClass('blender25')

class EPMV_OT_launch(bpy.types.Operator):
    bl_idname = "epmv.launch"
    bl_label = "ePMV"
    
    def execute(self, context):
        from ePMV import epmvGui
        epmvgui = epmvGui.epmvGui()
        epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender25')
        ##
        #define the default options
        epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                        useLog = False,doCloud=False,forceFetch=False)
        epmvgui.display()
        #create an empty object call "welcome to epmv ?"
        epmvobj = epmvgui.epmv.helper.newEmpty("Welcome to ePMV")
        return {'FINISHED'}

class EPMV_HT_icons(bpy.types.Header):
    bl_space_type = 'CONSOLE'#
    def draw(self, context):
        #if not prefs().show_header:
        #    return
        layout = self.layout
        layout.separator()
        layout.operator(EPMV_OT_launch.bl_idname)

def menu_draw(self, context):
    self.layout.operator(EPMV_OT_launch.bl_idname)#,icon="PLUGIN")
    
# creo il link al manuale
def menu_draw_map():
        url_manual_prefix=""
        url_manual_mapping = (("epmv.launch", "editors/edview/object"),)
        return url_manual_prefix, url_manual_mapping

classes = (
    EPMV_OT_launch,
    #EPMV_HT_icons
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_HT_header.append(menu_draw)
    #bpy.types.INFO_MT_add.append(menu_draw)
    bpy.utils.register_manual_map(menu_draw_map)
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

def test_ePMV():
    import os
    softdir = os.path.abspath(os.path.curdir)
    MGL_ROOT =softdir
    from ePMV import epmvGui
    epmvgui = epmvGui.epmvGui()
    epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender25')
    epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                            useLog = False,doCloud=False,forceFetch=False)
    epmvgui.display()
#test_ePMV()
# File "C:\Users\ludov\Tools\blender-2.80-windows64/MGLToolsPckgs\ePMV\epmvAdaptor.py", line 2146, in coarseMolSurface
#    isocontour.NO_COLOR_VARIABLE)