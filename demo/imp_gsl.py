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