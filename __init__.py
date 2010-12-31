# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 08:54:28 2010

@author: Ludovic Autin
"""

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
    """    

    if soft == 'blender':
        from ePMV.blender.blenderAdaptor import blenderAdaptor as adaptor
    elif soft=='c4d':
        from ePMV.cinema4d.c4dAdaptor import c4dAdaptor as adaptor
    elif soft=='maya':
        from ePMV.autodeskmaya.mayaAdaptor import mayaAdaptor as adaptor
#    elif soft == 'chimera':
#        from ePMV.Chimera.chimeraAdaptor import chimeraAdaptor as adaptor
#    elif soft == 'houdini':
#        from ePMV.houdini.houdiniAdaptor import houdiniAdaptor as adaptor
        
#    you can add here additional soft if an adaptor and an helper is available
#    use the following syntaxe, replace template by the additional hostApp
#    elif soft == 'template':
#        from Pmv.hostappInterface.Template.chimeraAdaptor import templateAdaptor as adaptor 
    #Start ePMV
    return adaptor(gui=gui,debug=debug)
