
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/interactive_demo.py is part of ePMV.

    ePMV is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ePMV.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
from ePMV import demo
dir = demo.__path__[0]+'/'
rec = "hsg1.pdbqt"
self.readMolecule(dir+rec)
self.displayCPK("hsg1")
self.displayCPK("hsg1",negate = True)
self.computeMSMS("hsg1",surfName='MSMShsg1')
lig = "ind.pdbqt"
self.readMolecule(dir+lig)
self.displayCPK("ind")

#just use the Extension->PyAutoDock menu to add scorer
#then add the Py4D tag : epmv_update to the ligand master object
#play around

#in order to play with AR:
#
#patt5='patt17'#left
#patt6='patt35'#front
#patt7='patt36'#right
#patt8='patt39'#back   
##['front', 'right','back','left','top','bot']
#why loadDevice didnt set the transfo_position correctly
#about the scaleFactor?
#self.art.patternMgr.loadDevice(name='head',type='cube4',width=40.,
#                               listPatt=['kanjiPatt','sampPatt1', 'sampPatt2','patt15' ],
#                                trans=[0.,0.,-30.],scaleFactor=1.)
#self.art.patternMgr.loadDevice(name='bott',type='cube4',
#							listPatt=[patt6,patt7,patt8,patt5],width=40.,
#							trans=[0.,0.,-30.],scaleFactor=1.)
##offset ?
#self.art.patternMgr.groups['head'].offset = [60.,0.,0.]
#self.art.patternMgr.groups['bott'].offset = [60.,0.,0.]
#
##self.loadPattern(['hiroPatt', 'kanjiPatt'], log=0)
##self.setWidth(['hiroPatt', 'kanjiPatt'], 40.0, log=0)
#
#geom = self.Mols[0].geomContainer.masterGeom
#self.setGeoms('head',[geom],log=0)#1oel
#geom1 = self.Mols[1].geomContainer.masterGeom
#self.setGeoms('bott',[geom1],log=0)#1oel
#

