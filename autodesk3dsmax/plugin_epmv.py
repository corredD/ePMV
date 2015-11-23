
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/autodesk3dsmax/plugin_epmv.py is part of ePMV.

    ePMV is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ePMV.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
# upyEPMVPlugin
import os
import sys
import ePMV
import upy
from PySide import QtGui, QtCore, shiboken

found = True
MGL_ROOT=upy.__path__[0]+"\\..\\"

sys.path.append(MGL_ROOT+os.sep+"PIL")
sys.path.append(MGL_ROOT+os.sep+"lib-tk")

upy.setUIClass()
from ePMV import epmvGui

#if 3dsMax not in the PATH add it
if "C:\\Program Files\\Autodesk\\3ds Max 2015" not in os.environ['PATH']:
    path = os.environ['PATH']
    os.environ['PATH'] = "C:\\Program Files\\Autodesk\\3ds Max 2015" + os.pathsep +  path


def upyEPMV_Execute(  ):
    #MGL_ROOT=""#"C:"+os.sep+"Users"+os.sep+"ludovic"+os.sep+"AppData"+os.sep+"Local"+os.sep+"Autodesk"+os.sep+"3dsMax"+os.sep+max_version+" - 64bit"+os.sep+"ENU"+os.sep+"plugins"+os.sep+"MGLToolsPckgs"
    epmvui = epmvGui.epmvGui(parent=None)
    print "init epmvGui",epmvui
    epmvui.setup(rep="epmv",mglroot=MGL_ROOT,host='3dsmax')
    print "setup gui MGLroot ",MGL_ROOT
    epmvui.epmv.Set(bicyl=True,use_progressBar = False,doLight = False,doCamera = False,
        useLog = False,doCloud=False,forceFetch=False)
    print "setup epmv"
    epmvui.display()
    print "ok display"
    return True

#app = QtGui.QApplication.instance()
#if not app:#
#	app = QtGui.QApplication([])
	
def main():		
    #MaxPlus.FileManager.Reset(True)#?
    upyEPMV_Execute(  )
    
if __name__ == '__main__':
	main()