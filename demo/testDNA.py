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
