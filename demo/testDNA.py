
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/testDNA.py is part of ePMV.

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
#delete water and heteroatoms
#1kx5:: MN*:;
mol = self.Mols[0]
dna_chains = mol.chains.get("I,J")
#dna_chains = mol.chains[0:2]
listeHB=epmv.getDNAHbonds(dna_chains,uniq=True)
print(len(listeHB))
epmv.displayDNAHbonds(listeHB)

mol = self.Mols[0]
#need to build the struts...look like the hbonds are not so nice...
paramDict={}
if 'distCutoff' not in paramDict:
    paramDict['distCutoff'] = 6 #residues min distance
if 'distCutoff2' not in paramDict:
    paramDict['distCutoff2'] = 5.0 #strut threshold distance
vStruts = self.buildStruts(mol,paramDict)
print(len(vStruts))
epmv.displayStruts(mol)
#then display it
