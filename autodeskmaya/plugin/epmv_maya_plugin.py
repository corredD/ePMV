"""
Name: 'Python Molecular Viewer GUI'
AutoDesk Maya: 2011
"""

__author__ = "Ludovic Autin"
__url__ = ["http://mgldev.scripps.edu/projects/ePMV/wiki/index.php/Main_Page",
           'http://mgldev.scripps.edu/projects/ePMV/update_notes.txt']
__version__="0.0.2a"
__doc__ = "ePMV v"+__version__
__doc__+"""\
Use maya as a molecular viewer

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
#import pdb
#MAYA import
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

import sys
import os
#cmds.confirmDialog( title='About ePMV', message=about, button=['OK'], 
#                           defaultButton='OK')
                           
#MGL_ROOT="/Library/MGLTools/1.5.6.up"

prefpath=cmds.internalVar(userPrefDir=True)
os.chdir(prefpath)
os.chdir(".."+os.sep)
softdir = os.path.abspath(os.curdir)
mgldirfile=prefpath+os.sep+"mgltoolsdir"
personalize = False
if os.path.isfile(mgldirfile) :
    f=open(mgldirfile,'r')
    MGL_ROOT=f.readline()
    f.close()
else :
    cmds.confirmDialog( title='ePMV', message="ePMV is not correctly installed.\n try to resinstall\n"+mgldirfile, button=['OK'], 
                           defaultButton='OK')
print(MGL_ROOT)
ICONSDIR=MGL_ROOT+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+os.sep+"images"+os.sep+"icons"+os.sep
print(ICONSDIR)
#register plugin dir
#this is handle by the user
#plugpath=os.environ["MAYA_PLUG_IN_PATH"].split(":")
#uidir =MGL_ROOT+os.sep+"MGLToolsPckgs"+os.sep+"Pmv"+os.sep+"hostappInterface"+os.sep+"autodeskmaya"+os.sep+"plugin"
#if uidir not in plugpath:
#    os.environ["MAYA_PLUG_IN_PATH"] = os.environ["MAYA_PLUG_IN_PATH"]+":"+uidir

#add to syspath
sys.path.append(MGL_ROOT+'/MGLToolsPckgs')
if sys.platform == "win32":
    sys.path.append(MGL_ROOT+os.sep+'MGLToolsPckgs'+os.sep+'PIL')
else :
    sys.path[0]=(MGL_ROOT+'/lib/python2.5/site-packages')
    sys.path.insert(0,MGL_ROOT+'/lib/python2.5/site-packages/PIL')
    sys.path.append('/Library/Python/2.5/site-packages/')

kPluginCmdName = "ePMV"
print(kPluginCmdName)

import upy
upy.setUIClass('maya')
from ePMV import epmvGui

# command
class scriptedCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
    def doIt(self,argList):
        print(argList)
        epmvui = epmvGui.epmvGui()
        epmvui.setup(rep="epmv",mglroot=MGL_ROOT,host='maya')
        epmvui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                useLog = False,doCloud=False,forceFetch=False)
        epmvui.CreateLayout()

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( scriptedCommand() )

# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
#        createShelf()
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
        raise

##add in the shelf:
#import maya
#import maya.OpenMaya as om
#maya.cmds.ePMV2()
#epmv = maya.mv.values()[0]
#
#script mode :
#import ePMV
#ePMV.setUIClass('maya')
#from ePMV import epmvGui
#epmvui = epmvGui()
#epmvui.setup(rep=dname,mglroot=MGL_ROOT,host='maya')
#epmvui.CreateLayout()
