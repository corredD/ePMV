
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/demo/surface_per_chain.py is part of ePMV.

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
#ms/cms per chain#self or epmv.mv is the molecular viewer#epmv is the adaptor#epmv.helper is the host helper function#epmv.gui is the ui interface#self.Mols is the array of currently loaded molecule from 0 to n#you can get a molecule from her name#special Fix for Blender.host=""try :    print (epmv)    host = epmv.helper.hostexcept :    #what the current host    import upy    host = upy.retrieveHost()    if host.find("blender")!= -1 :        import bpy        epmv = bpy.mv["epmv"]        self = epmv.mv        mol = epmv.gui.current_mol #or use a name#molname = "2plv"#mol = self.getMolFromName(molname)pradius = 1.5density = 3.0doMSMS = Truegridsize=32iso=7.1res=-0.3doCMS = True#we compute and create a geometry for every chain in the moleculefor chain in mol.chains :    parent = mol.geomContainer.masterGeom.chains_obj[chain.name]    if doMSMS:        surfname=mol.name+chain.name+"MSMS"        self.computeMSMS(chain,surfName=surfname,perMol=0,                             pRadius=pradius,density = density)        #epmv will triger the creation of the geomtry in the host        #to color you can color with custom color, or use a schem#        self.color(chain,[(1,1,0)],[surfname])        self.colorByChains(chain,[surfname])#        self.colorByResidueType(chain,[surfname])    if doCMS :        cmsname=mol.name+chain.name+"CMS"        geom=epmv.coarseMolSurface(chain.residues.atoms,[gridsize,gridsize,gridsize],                                        isovalue=iso,resolution=res,                                        name=cmsname)        mol.geomContainer.geoms[cmsname]=geom        obj=epmv.helper.createsNmesh(cmsname,geom.getVertices(),None,                                      geom.getFaces(),proxyCol=True,smooth=True)        epmv._addObjToGeom(obj,geom)        epmv.helper.addObjectToScene(epmv.helper.getCurrentScene(),                                      obj[0],parent=parent)#        self.color(chain,[(1,1,0)],[cmsname])        self.colorByChains(chain,[cmsname])#        self.colorByResidueType(chain,[cmsname])                                      #we can also apply them some color...#in order to do it per residues we can add another forloop#for chain in mol.chains:#    for res in chain.residues:#        surfname = mol.name+chain.name+res.name+"MSMS"#        self.computeMSMS(res,surfName=surfname,perMol=0,#                             pRadius=pradius,density = density)#        self.colorByResidueType(res,[surfname])#.....#print self.Mols[0].geomContainer.geoms["MSMS-MOL3fwm"]#self.colorByDomains(self.Mols[0].name+":::",["MSMS-MOL3fwm"])#self.colorByDomains.method = "SCOP"#'SCOP', 'CATH', 'dp' and 'pdp'#self.colorByDomains.forcedomain = True