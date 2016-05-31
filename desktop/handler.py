# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import qxrd
import numpy as np

import plottool
import os
import time

def openXRD(filename):
    """
   Opens an XRD file and returns two 1D array for 2theta and Intensity
   possible formats: TXT, PLV, DIF, MDI   ....   more to come
    """

    if filename.endswith(".plv"): 
        jump=50
        XRDdata = open(filename, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
       
    elif filename.endswith(".txt"):
        jump=7
        XRDdata = open(filename, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
        
    elif filename.endswith(".dif") or filename.endswith(".mdi"):
        dif = open(filename, 'r').readlines()
        paramline = dif[1]
        start, step, unknown, target, Lambda, stop, number = paramline.split()
        start=float(start)
        step=float(step)
        stop=float(stop)
        angle = np.arange(start, stop+step, step)
        diff = np.zeros_like(angle)
        #loop bellow reads data values of all but last line which all contain 8 entries
        for i in range(2,len(dif)-1):
            dataline = dif[i]
            dataline=dataline.split()
            linenumber = i-2
            for j in range(0,8):
                diffindex = ((linenumber)*8)+j
                diff[diffindex]=float(dataline[j])
                
        # bellow reads last line which can contain less than 8 entries
        lastline = dif[len(dif)-1]
        lastline = lastline.split()

        for i in range(0,len(lastline)):
             diffindex = ((len(dif)-3)*8)+i
             diff[diffindex]=float(lastline[i])

    return (angle, diff) #, target, Lambda  needs to be coded in txt and plv

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


userData = openXRD(os.path.join(datafilepath, datafilename))

results, BG, calcdiff = qxrd.Qanalyze(userData, difdata, selectedphases, InstrParams)

print "Total computation  time = %.2fs" %(time.time()-t0)
plot = plottool.overplotgraph(userData,BG,calcdiff, results[0:min(10,len(results))], datafilename)

#print plot, results

