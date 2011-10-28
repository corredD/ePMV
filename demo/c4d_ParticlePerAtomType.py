# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 13:38:45 2011

@author: Ludovic autin

This script will generate a Particle System group per Atom type, as well as the TP geometry.
In the viewport simply create pyrocluster material and shader and render, you should see  a volume representation of the molecule

"""
from Pmv.pmvPalettes import AtomElements
listea = ["CA","C","O","N"]
pg=[]
for at in listea:
    ats = self.Mols[0].allAtoms.get(at+"*")
    PS = epmv.helper.particle(at,ats.coords,group_name=at,
                              radius=ats.radius,
                              color=AtomElements[at[0]])
    g = epmv.helper.newTPgeometry("pyro"+at,group = PS)
    pg.append(g)
self.Mols[0].has_particls = True
self.Mols[0].particleg=pg
