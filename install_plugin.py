
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/install_plugin.py is part of ePMV.

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

MGL_ROOT=""
doit=True
try :
    import ePMV
    path = ePMV.__path__[0]
    print("path",path)
#    print os.path.abspath(path)
    os.chdir(os.path.abspath(path))
    os.chdir('../')
    MGL_ROOT = os.path.abspath(os.curdir)
    doit=False
except:
    doit=True
#print MGL_ROOT
if doit :
    ismaya = False
    try :
        import maya
        ismaya=True
    except:
        ismaya=False
    if ismaya:
        import maya.cmds as cmds
        MGL_ROOT = cmds.fileDialog2(fileMode=3, dialogStyle=1,
                                        cap="what is the  MGLToolsPckgs directory?")
        print(MGL_ROOT)
        #verify if its MGLToolsPCkgs or the up dir
        MGL_ROOT = str(MGL_ROOT[0])
        print(MGL_ROOT)
        if MGL_ROOT.find("MGLToolsPckgs") == -1:
            if not os.path.exists(MGL_ROOT+os.sep+"MGLToolsPckgs"):
                MGL_ROOT = cmds.fileDialog2(fileMode=3, dialogStyle=1,
                                        cap="what is the  MGLToolsPckgs directory?")
                MGL_ROOT = str(MGL_ROOT[0])
    else:
        print(__file__)
        curpath = os.path.abspath(__file__) #this should give pathtoMGL/MGLToolsPckgs/ePMV/install.py
#        print "find",curpath.find("MGLToolsPckgs")
        if curpath.find("MGLToolsPckgs") == -1 : #cant find MGLToolsPCkgs 
#            print "yes"
            import Blender
            txt = Blender.Text.Get(__file__)
            curpath = txt.getFilename()
#            print "curpath",curpath
#            print os.path.dirname(curpath)
        if os.path.isfile(curpath):
            os.chdir(os.path.dirname(curpath))
        else :
            os.chdir(os.path.abspath(curpath))
        os.chdir('../')
        MGL_ROOT = os.path.abspath(os.curdir)
#        print "dir",dir
print(MGL_ROOT)
sys.path.append( MGL_ROOT )
from ePMV.installer import Installer

print("MGL",MGL_ROOT)
if __name__ == '__main__':
    print(__name__)
    import os
    import sys
#    print __file__
#    curpath = os.path.abspath(__file__) #this should give pathtoMGL/MGLToolsPckgs/ePMV/install.py
    os.chdir(MGL_ROOT)
    os.chdir('../')
    MGL_ROOT = os.path.abspath(os.curdir)
    print(MGL_ROOT)
    inst = Installer(mgl=MGL_ROOT)
    if sys.platform == 'win32':
        inst.patchPMV()
    from ePMV.installer import InstGui
    gui = InstGui(title="Install ePMV")
    gui.setup(inst=inst,mgl=MGL_ROOT)
    gui.display()