
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/pmv_dev/strutsBondBuilder.py is part of ePMV.

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
## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Author:  Ruth Huey
#
# Copyright: M. Sanner TSRI 2005
#
#############################################################################

#
# $Header: /opt/cvs/python/packages/share1.5/MolKit/hydrogenBondBuilder.py,v 1.8.2.1 2011/04/13 18:07:36 rhuey Exp $
#
# $Id: hydrogenBondBuilder.py,v 1.8.2.1 2011/04/13 18:07:36 rhuey Exp $
#

"""
This module implements the HydrogenBondBuilder class which builds hydrogen
bonds between appropriate atoms.

"""

from MolKit.molecule import Atom, AtomSet, HydrogenBond
from MolKit.distanceSelector import DistanceSelector
class BitSet :
    def __init__(self,):
        self.dic={}
        
    def set(self,id):
        self.dic[id] = True
    
    def clear(self,id):
        self.dic.pop(id)
    
    def get(self,id):
        if  self.dic.get(id) is None :
            return False
        else :
            return self.dic.get(id)
        #return False if self.dic.get(id) is None else self.dic.get(id)

class strutsBond:
    """Class to represent a strut bond. Inherits from Bond"""

      
    def __init__(self, donAt,  accAt, dlen=None, theta=None, phi=None, 
                torsion=None, energy=None,  
                name='NoName', typ=None, check=1):
        """
        donAt: heavy atom which 'donates' hydrogen to bond
        accAt: heavy atom which 'accepts' hydrogen from bond
        dlen: distance between donAt + accAt
        theta: donAt, hAt, accAt angle
        phi: hAt, accAt angle, accAtNeighbor
        torsion: angle between normals to d-h-a and h-a-aa
        energy: calc from j.Mol.Graphics Modell., 2001, Vol19, No.1, p62
            energy=Vo{5(do/d)**12-6(do/d)**10}F(theta,phi,gamma)
                different forms of F are used depending on whether
                donAt +  accAt are sp2 or sp3 hybridized 
                gamma is torsion defined by donAt-hAt-accAt-accAtNeighbor
        if check: 
            atom1.isBonded returns 1 if hbond to atom2 already exists 
                 which raises an exception
        """
        assert isinstance(donAt, Atom)
        assert isinstance(accAt, Atom)
        #assert isinstance(hAt, Atom)
        if check: 
            bonded = self.checkIsBonded(donAt, accAt)
            if bonded:
                msg = donAt.full_name() + ' is already bonded to '+ accAt.full_name()
                raise RuntimeError(msg)
        self.donAt = donAt
        self.accAt = accAt
        self.dlen = dlen
        self.theta = theta
        self.phi = phi
        self.torsion = torsion
        self.energy = energy
        self.type = typ          

    def checkIsBonded(self, donAt, accAt):
        if not hasattr(donAt, 'struts'): return 0
        if not hasattr(accAt, 'struts'): return 0
        for b in donAt.struts:
            if id(b.donAt)==id(donAt) and id(b.accAt)==id(accAt):
                return 1
            if id(b.accAt)==id(donAt) and id(b.donAt)==id(accAt):
                return 1
        return 0

    def __repr__(self):
        return "<%s instance '%s' - 'None'....'%s'>" % \
                   ( self.__class__.__name__, self.donAt.full_name(),
                      self.accAt.full_name())

    


#needed for some math..
import numpy
import math
import sys

#def applyTransformation(pt, mat):
#    pth = [pt[0], pt[1], pt[2], 1.0]
#    return Numeric.dot(mat, pth)[:3]
#
#
#def getTransformedCoords(atom):
#    # when there is no viewer, the geomContainer is None
#    if atom.top.geomContainer is None:
#        return atom.coords
#    g = atom.top.geomContainer.geoms['master']
#    c = applyTransformation(atom.coords, g.GetMatrix(g))
#    return  c.astype('f')


distCutoff=6    #H-Acc Distance cutoff to mean 2.06 std dev 0.19
                    #@@ distCutoff2 increased 4/2011 
                    #   based on data: www.biochem.ucl.ac.uk/bsm/atlas/mc.html
distCutoff2=4.0    #Donor-Acc Distance cutoff @@mean 2.98 std dev 0.17@@

class StrutsBondBuilder:
    """
    object which can build  bonds between atoms according
    to their coords and atom type
    """

    def __init__(self, distCutoff=distCutoff, distCutoff2=distCutoff2):
        d = self.paramDict = {}
        d['distCutoff'] = distCutoff
        d['distCutoff2'] = distCutoff2
        self.delta = distCutoff


    def reset(self, ats):
        tops = ats.top.uniq()
        for mol in tops:
            for a in mol.allAtoms:
                if hasattr(a, 'struts'):
                    for item in a.struts:
                        del item
                    delattr(a, 'struts')

    
    
    
    def build(self, group1, reset=True, paramDict=None):
        """atDict <- build(group1, group2, reset, paramDict=None, **kw):
            group1: atoms 
            group2: atoms 
            reset: remove all previous hbonds, default True!

            paramDict: a dictionary with these keys and default values
            distCutoff: 2.25  hydrogen--acceptor distance
            distCutoff2: 3.00 donor... acceptor distance
           """
        #setup parameter dictionary
        if paramDict is None:
            paramDict = self.paramDict

        #process each group
        #group1
        if group1.__class__!=Atom:
            group1 = group1.findType(Atom)
            #print "now group1=", group1.full_name()
            if not len(group1):
                return "ERROR"  #@@ OR WHAT?

        if reset:
            #do optional reset: remove all prior hbonds 
            self.reset(group1)
        self.delta = paramDict['distCutoff']
        #Build, this added the struts attribute to atoms
        self.vStruts = self.calculateStruts(group1.top, group1, group1.get("CA,P,O5'"), 
                               bs1=None, bs2=None, thresh=paramDict['distCutoff2'], 
                                delta=paramDict['distCutoff'], allowMultiple=False)
        return self.vStruts


    def makeBonds(self, at1, at2):
#        if hasattr(at1, 'struts') and len(k.struts):
#            return
#        if hasattr(at2, 'struts') and len(k.struts):
#            return         
        newSB = strutsBond(at1, at2)
        if not hasattr(at1, 'struts'):
            at1.struts=[]
        if not hasattr( at2, 'struts'):
            at2.struts=[]
        at1.struts.append(newSB)
        at2.struts.append(newSB)

    def measure_distance(self,c0,c1,vec=False):
        """ measure distance between 2 point specify by x,y,z
        c0,c1 should be Numeric.array"""
        d = numpy.array(c1) - numpy.array(c0)
        s = numpy.sum(d*d)
        if vec :
            return d,math.sqrt(s)
        else :
            return s
    
    def strutPoint(self,i, j, n) :
        #ipt = i * (2 * n - i - 1) / 2 + j - i - 1
        if j < i :
            return j * (2 * n - j - 1) / 2 + i - j - 1
        else :
            return i * (2 * n - i - 1) / 2 + j - i - 1
        
    
    def setStrut(self,i, j, n, vCA, bs1, bs2,vStruts,bsStruts,
                 bsNotAvailable,bsNearbyResidues,delta) :
        a1 = vCA[i]
        a2 = vCA[j]
        a1index=a1.top.allAtoms.index(a1)
        a2index=a2.top.allAtoms.index(a2)
        #if not bs1.get(a1index) or not bs2.get(a2index):
        #  return
        vStruts.append([a1, a2])
        self.makeBonds(a1, a2)
        bsStruts.set(a1)
        bsStruts.set(a2)
        k1 = max(0, i - delta)
        while k1 <= i + delta and k1 < n :
            k2 = max(0, j - delta)
            while k2 <= j + delta and k2 < n :
                if (k1 == k2):
                    k2 = k2 + 1
                    continue
                ipt = self.strutPoint(k1, k2, n)
                #if not bsNearbyResidues.get(ipt):
                bsNotAvailable.set(ipt)
                k2 = k2 + 1
            k1 = k1 + 1
        return vStruts,bsStruts,bsNotAvailable
    
    def calculateStruts(self,modelSet, atoms, vCA, bs1=None, bs2=None, thresh=7.0, 
                        delta=6, allowMultiple=False):
        vStruts = [] #the output vectorAtomSet()
        thresh2 = thresh * thresh #use distance squared for speed
    
        #TODO  CHECK IMPLEMENT BITSETS
        delta = int(delta)
        n = len(vCA)
        nEndMin = 3
        # We set bitsets that indicate that there is no longer any need to
        # check for a strut. We are tracking both individual atoms (bsStruts) and
        # pairs of atoms (bsNotAvailable and bsNearbyResidues)
        
        #is it liike the bhtree???
        bsStruts = BitSet()         # [i]
        bsNotAvailable = BitSet()   # [ipt]
        bsNearbyResidues = BitSet() # [ipt]
        
        # check for a strut. We are going to set struts within 3 residues
        # of the ends of biopolymers, so we track those positions as well.
        
        #a1 = vCA[0]#Atom
        #a2 = Atom()
        #nBiopolymers = modelSet.getBioPolymerCountInModel(a1.modelIndex); #is it like nb chain ?
        nBiopolymers = len(modelSet.chains)
        #int[][] biopolymerStartsEnds = new int[nBiopolymers][nEndMin * 2];
        biopolymerStartsEnds = numpy.zeros((nBiopolymers,nEndMin * 2),'i')
        #for (int i = 0; i < n; i++) {
        for i in range(n) :
            a1 = vCA[i]
            polymerIndex = a1.parent.parent.number #chain a1.getPolymerIndexInModel()
            monomerIndex = a1.parent.parent.residues.index(a1.parent)        #residue a1.getMonomerIndex();
            bpt = monomerIndex
            if (bpt < nEndMin):
                biopolymerStartsEnds[polymerIndex][bpt] = i + 1
            bpt = len(a1.parent.parent.residues) - monomerIndex - 1
            if (bpt < nEndMin):
                biopolymerStartsEnds[polymerIndex][nEndMin + bpt] = i + 1;
    
        # Get all distances.
        # For n CA positions, there will be n(n-1)/2 distances needed.
        # There is no need for a full matrix X[i][j]. Instead, we just count
        # carefully using the variable ipt:
        #
        # ipt = i * (2 * n - i - 1) / 2 + j - i - 1
    
        #float[] d2 = new float[n * (n - 1) / 2];
        d2 = numpy.zeros(n * (n - 1) / 2,'f')
#        print "number of CA",n
        for i in range(n) :
            a1 = vCA[i]
            for j in range(i+1,n):
                ipt = self.strutPoint(i, j, n)
                a2 = vCA[j]
                resno1 = a1.parent.parent.residues.index(a1.parent)#a1.getResno();
                polymerIndex1 = a1.parent.parent.number#a1.getPolymerIndexInModel();
                resno2 = a2.parent.parent.residues.index(a2.parent)#a2.getResno();
                polymerIndex2 = a2.parent.parent.number#a2.getPolymerIndexInModel();
                #print polymerIndex1,polymerIndex2,(polymerIndex1 == polymerIndex2)
                #print resno1,resno2,delta,(abs(resno2 - resno1) < delta)
                if (polymerIndex1 == polymerIndex2) and (abs(resno2 - resno1) <= delta):
                    bsNearbyResidues.set(ipt)
                #else :
                #    print i,j,ipt,polymerIndex2,polymerIndex1,resno2,resno1,abs(resno2 - resno1),delta
                d = d2[ipt] = self.measure_distance(a1.coords,a2.coords)#a1.distanceSquared(a2);
                if (d >= thresh2):
                      bsNotAvailable.set(ipt)
                      #print len(bsNearbyResidues.dic.keys())
        # Now go through 5 spheres leading up to the threshold
        # in 1-Angstrom increments, picking up the shortest distances first
        # this a long one.....
        t = 5
        while t >=0 :
        #for (int t = 5; --t >= 0;) { # loop starts with 4
            thresh2 = (thresh - t) * (thresh - t);
            for i in range(n) :
                if allowMultiple or not bsStruts.get(vCA[i]):
                    #sys.stdout.write("%d,%d,%d\n" % ( t,i,n))
                    for j in range(i+1,n):
                        ipt = self.strutPoint(i, j, n)
                        if (not bsNotAvailable.get(ipt)) and (not bsNearbyResidues.get(ipt)) \
                          and (allowMultiple or not bsStruts.get(vCA[j])) and (d2[ipt] <= thresh2):
                            #sys.stdout.write("setStrut,%d,%d,%d\n" % ( i,j,ipt))
#                            print i,j,ipt,len(vStruts),bsNearbyResidues.dic.has_key(ipt)
                            vStruts,bsStruts,bsNotAvailable = self.setStrut(i, j, n, 
                                                vCA, bs1, bs2, 
                                                vStruts, bsStruts, bsNotAvailable,
                                                bsNearbyResidues, delta)
            t=t-1
#        print len(vStruts)
        # Now find a strut within nEndMin (3) residues of the end in each
        # biopolymer, but only if it is within one of the "not allowed"
        # regions - this is to prevent dangling ends to be connected by a
        # very long connection
        okN = False
        okC = False
        for b in range(nBiopolymers):
          # if there are struts already in this area, skip this part
            for k in range(nEndMin * 2):
                i = biopolymerStartsEnds[b][k] - 1
                if (i >= 0 and bsStruts.get(vCA[i])) :
                    for j in range(nEndMin):#(int j = 0; j < nEndMin; j++) {
                        pt = (k / nEndMin) * nEndMin + j
                        i = biopolymerStartsEnds[b][pt] - 1
                        if i >= 0:
                            bsStruts.set(vCA[i]);
                        biopolymerStartsEnds[b][pt] = -1
            #print (biopolymerStartsEnds[b][0] == -1 and biopolymerStartsEnds[b][nEndMin] == -1)
            if (biopolymerStartsEnds[b][0] == -1 and biopolymerStartsEnds[b][nEndMin] == -1):
                continue;
            okN = False;
            okC = False;
            iN = 0;
            jN = 0;
            iC = 0;
            jC = 0;
            minN = 99999999999999.;
            minC = 99999999999999.;
            for j in range(n):
                for k in range(nEndMin * 2):
                    i = biopolymerStartsEnds[b][k] - 1
                    if (i == -2) :
                        k = (k / nEndMin + 1) * nEndMin - 1
                        continue
                if (j == i or i == -1):
                    continue
                ipt = self.strutPoint(i, j, n);
                if (bsNearbyResidues.get(ipt) or d2[ipt] > (minN if k < nEndMin else minC)):
                    continue
                if (k < nEndMin) :
                    if (bsNotAvailable.get(ipt)):
                        okN = True
                    jN = j
                    iN = i
                    minN = d2[ipt]
                else :
                    if (bsNotAvailable.get(ipt)):
                          okC = True
                    jC = j
                    iC = i
                    minC = d2[ipt]
            if (okN):
                vStruts,bsStruts,bsNotAvailable =self.setStrut(iN, jN, n, vCA, bs1, bs2, vStruts, bsStruts, bsNotAvailable,
                bsNearbyResidues, delta);
            if (okC):
                vStruts,bsStruts,bsNotAvailable =self.setStrut(iC, jC, n, vCA, bs1, bs2, vStruts, bsStruts, bsNotAvailable,
                bsNearbyResidues, delta);
        return vStruts

