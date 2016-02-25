
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import phaseanalyze2 as QUANT
import numpy as np


#############################################################################################

def openXRD(name):
    """
   Opens an XRD file and returns two 1D array for 2theta and Intensity
   possible formats: TXT, PLV, DIF, MDI   ....   more to come
    """

    if name.endswith(".plv"): 
        jump=50
        XRDdata = open(name, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
       
    elif name.endswith(".txt"):
        jump=7
        XRDdata = open(name, 'r').readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
        
    elif name.endswith(".dif") or name.endswith(".mdi"):
        dif = open(name, 'r').readlines()
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
        print lastline
        for i in range(0,len(lastline)):
             diffindex = ((len(dif)-3)*8)+i
             diff[diffindex]=float(lastline[i])
    else:     
        print "file format error: plv, txt, dif, mdi required."
        
    return angle, diff #, target, Lambda  needs to be coded in txt and plv

#############################################################################################




filepath1='/home/philippe/Documents/Projects/AutoQuant/XRD_data/'
namesample = "Mix3B-film.txt"
filepath2='/home/philippe/Documents/Projects/AutoQuant/'
DBname="Final_AutMin-Database-difdata.txt"
phaselistname = 'AutMin-phaselist-final.csv'
filename1= filepath1 + namesample

difdata = open((filepath2 + DBname), 'r').readlines()
phaselist = open((filepath2 + phaselistname), 'r').readlines()
twoT, diffrac = openXRD(filename1)
results, plot = QUANT.PhaseAnalyze(twoT, diffrac ,difdata,phaselist)

print plot
