# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 08:54:28 2010

@author: Ludovic Autin
"""
import os
if not os.path.isfile(os.path.abspath(__path__[0])+os.sep+"version.txt"):
    f=open(os.path.abspath(__path__[0])+os.sep+"version.txt","w")
    f.write("0.0.0")
    f.close()
f = open(os.path.abspath(__path__[0])+os.sep+"version.txt","r")
__version__ = f.readline()#"0.6.304"
f.close()
#__version__ = "0.5.125"

def epmv_start(soft,gui=False,debug=0):
    """
    Initialise a embeded PMV cession in the provided hostApplication.
    
    @type  soft: string
    @param soft: name of the host application
    @type  debug: int
    @param debug: debug mode, print verbose
    
    @rtype:   epmvAdaptor
    @return:  the embeded PMV object which consist in the adaptor, the molecular
    viewer and the helper.
    #whatabout tk and Qt?
    """    
    import upy
    if soft is None :
        soft = upy.retrieveHost()
    if soft == 'blender24':
        from ePMV.blender.v24.blenderAdaptor import blenderAdaptor as adaptor
    elif soft == 'blender25':
        from ePMV.blender.v25.blenderAdaptor import blenderAdaptor as adaptor
    elif soft=='c4d':
        from ePMV.cinema4d.c4dAdaptor import c4dAdaptor as adaptor
    elif soft=='maya':
        from ePMV.autodeskmaya.mayaAdaptor import mayaAdaptor as adaptor
    elif soft=='3dsmax':
        from ePMV.autodesk3dsmax.maxAdaptor import maxAdaptor as adaptor
    elif soft=='softimage':
        from ePMV.softimage.softimageAdaptor import softimageAdaptor as adaptor
    else :
        from ePMV.epmvAdaptor import epmvAdaptor as adaptor
#    elif soft == 'chimera':
#        from ePMV.Chimera.chimeraAdaptor import chimeraAdaptor as adaptor
#    elif soft == 'houdini':
#        from ePMV.houdini.houdiniAdaptor import houdiniAdaptor as adaptor
        
#    you can add here additional soft if an adaptor and an helper is available
#    use the following syntaxe, replace template by the additional hostApp
#    elif soft == 'template':
#        from Pmv.hostappInterface.Template.chimeraAdaptor import templateAdaptor as adaptor 
    #Start ePMV
#    print ("start",adaptor,"soft",soft)
    return adaptor(gui=gui,debug=debug)


def get_ePMV():
    """
    Retrieve the embeded PMV session.

    @rtype:   object
    @return:  the current ePMV session
    """    
    import upy
    uiclass = upy.getUIClass()
    hclass = upy.getHelperClass()    
    #epmv = None    
    #c4d use the current document name
    epmv = uiclass._restore('mv','epmv')
    if epmv is None :
        dname = hclass.getCurrentSceneName()
        epmv = uiclass._restore('mv',dname)
    return epmv
