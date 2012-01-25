# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 15:10:57 2011

@author: -
"""
import SOAPpy

server = SOAPpy.SOAPProxy("http://www.pdb.org/pdb/services/pdbws")
#A domain prediction method (one of 'SCOP', 'CATH', 'dp' and 'pdp' -- may be null if all are required)
def getDomains(id):
    res = server.getDomainFragments("3fwm","A","pdp")
    len(res)