
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/imp_gsl.py is part of ePMV.

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
Created on Thu Oct 27 12:23:12 2011

@author: ludovic autin
http://www.integrativemodeling.org/1.0/doc/html/IMP_gsl_examples.html
"""
MGLTOOLS = '/Users/ludo/Library/Preferences/MAXON/CINEMA 4D R12_C333CB6C/plugins/ePMV/mgl64//MGLToolsPckgs/'
IMPPATH = MGLTOOLS+"IMP_64"

import sys
sys.path.append(IMPPATH)
sys.path.append(IMPPATH+"/lib")

import IMP, IMP.test
import IMP.core
import IMP.gsl
import IMP.algebra

m= IMP.Model()
d0= IMP.core.XYZ.setup_particle(IMP.Particle(m), IMP.algebra.Vector3D(0,0,0))
d1= IMP.core.XYZ.setup_particle(IMP.Particle(m), IMP.algebra.Vector3D(3,4,5))
d0.set_coordinates_are_optimized(True)
d1.set_coordinates_are_optimized(True)

dist= IMP.core.DistanceRestraint(IMP.core.Harmonic(1, 1), d0, d1)
m.add_restraint(dist)

opt = IMP.gsl.Simplex(m)
opt.set_minimum_size(.000001)
opt.set_initial_length(1)
e = opt.optimize(1000000)
print IMP.core.get_distance(d0, d1)