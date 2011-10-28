# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 08:32:29 2011

@author: Ludovic Autin
From http://www.integrativemodeling.org/1.0/doc/html/IMP_em_examples.html

"""
MGLTOOLS = '/Users/ludo/Library/Preferences/MAXON/CINEMA 4D R12_C333CB6C/plugins/ePMV/mgl64//MGLToolsPckgs/'
IMPPATH = MGLTOOLS+"IMP_64"

import sys
sys.path.append(IMPPATH)
sys.path.append(IMPPATH+"/lib")

import IMP.em
import IMP.core
import IMP.atom
IMP.set_log_level(IMP.SILENT)
m= IMP.Model()
#1. setup the input protein
##1.1 select a selector.
sel=IMP.atom.NonWaterPDBSelector()
##1.2 read the protein
mh=IMP.atom.read_pdb(IMP.em.get_example_path("input.pdb"),m,sel)
ps=IMP.Particles(IMP.core.get_leaves(mh))
IMP.atom.add_radii(mh)
epmv.gui.loadPDB(IMP.em.get_example_path("input.pdb"))

#2. read the density map
resolution=8.
voxel_size=1.5
dmap=IMP.em.read_map(IMP.em.get_example_path("input.mrc"),IMP.em.MRCReaderWriter())
dmap.get_header_writable().set_resolution(resolution)
epmv.gui.loadDATA(IMP.em.get_example_path("input.mrc"))
#3. calculate the cross correlation between the density and the map
print "The cross-correlation score is:",1.-IMP.em.compute_fitting_score(ps,dmap)
#4. add a fitting restraint
r= IMP.em.FitRestraint(ps, dmap)
m.add_restraint(r)
print "The fit of the particles in the density is:",r.evaluate(False)

p0=IMP.Particle(m)
d0= IMP.core.XYZR.setup_particle(p0)
xd0= IMP.core.XYZ.decorate_particle(p0)

pm = mh.get_particle()
test = mh.get_as_xyz()
dm = test.setup_particle(pm)
xdm = test.decorate_particle(pm)

c= IMP.container.ListSingletonContainer(IMP.core.create_xyzr_particles(m, 20, 5))