
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/renderMaya.py is part of ePMV.

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
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 11:48:14 2011

@author: -
"""
from maya import mel
from maya import cmds
startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
cmds.progressBar( gMainProgressBar,
                                edit=True,
                                beginProgress=True,
                                isInterruptable=True,
                                status="Rendering...",
                                maxValue=endFrame)

for i in range(startFrame,endFrame):
    if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
        break
    cmds.currentTime( i )
    cmds.render()
    cmds.progressBar(gMainProgressBar, edit=True, step=1)
cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

print ("Completed rendering of " + str((endFrame - startFrame) + 1) + " frames.\n");


