# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import qxrd
import qxrdtools
import numpy as np

import plottool
import os
import time

datafilepath='XRD_data'
# datafilename = "Forsterite__R040018-1__Powder__Xray_Data_XY_Processed__3027.txt"
datafilename = "Mix2D-film.txt"
DBfilepath='databases'
DBname="difdata-rockforming.txt"
#phaselistname = 'Laure-mineral_list.csv'
phaselistname = 'difdata-rockforming_inventory.csv'


InstrParams = {"Lambda": 0, "Target": 'Cu', "FWHMa": 0.0022, "FWHMb": 0.2471}

# datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

t0=time.time()
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
selectedphases = []
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
for i in range (1, len(phaselist)):
    name, code = phaselist[i].split('\t')
    code = int(code)
    selectedphases.append((name,code))

file = os.path.join(datafilepath, datafilename)
blob = open(file, 'r')

userData = qxrdtools.openXRD(blob, os.path.join(datafilepath, datafilename))
# userData = qxrdtools.openXRD(os.path.join(datafilepath, datafilename), os.path.join(datafilepath, datafilename))

results, BG, calcdiff = qxrd.Qanalyze(userData, difdata, selectedphases, InstrParams)

print "Total computation  time = %.2fs" %(time.time()-t0)
plot = plottool.overplotgraph(userData,BG,calcdiff, results[0:min(10,len(results))], datafilename)

#print plot, results

