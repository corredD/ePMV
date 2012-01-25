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


