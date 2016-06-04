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
# datafilename = "CalciteP-film.plv"
datafilename = "Mix3D-film.txt"
DBfilepath=''
DBname="difdata-rockforming.txt"
phaselistname = 'test_list.csv'

InstrParams = {"Lambda": 0, "Target": '', "FWHMa": -0.001348, "FWHMb": 0.352021}

# datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

t0=time.time()
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
selectedphases = []
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
for i in range (1, len(phaselist)):
    name, code = phaselist[i].split('\t')
    code = int(code)
    selectedphases.append((name,code))


userData = qxrdtools.openXRD(os.path.join(datafilepath, datafilename), os.path.join(datafilepath, datafilename))

results, BG, calcdiff = qxrd.Qanalyze(userData, difdata, selectedphases, InstrParams)

print "Total computation  time = %.2fs" %(time.time()-t0)
plot = plottool.overplotgraph(userData,BG,calcdiff, results[0:min(10,len(results))], datafilename)

#print plot, results

