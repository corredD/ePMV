
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/c4d_ParticlePerAtomType.py is part of ePMV.

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
