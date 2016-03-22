# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import Conductor
import numpy as np
import os
import time
from Tkinter import *
from tkFileDialog import askopenfilename



#datafilepath='/home/philippe/Documents/Projects/Python/Autoquant-Web/XRD_data'
#datafilename = "Mix3B-film.txt"
DBfilepath='/home/philippe/Documents/Projects/Python/Autoquant-Web'
DBname="reduced_difdata.txt"
phaselistname = 'phaselist2.csv'
Lambda = ''
Target = ''


datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

Tk().withdraw()
t0=time.time()
difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
selectedphases = ["Actinolite", "Turdite", "AlbiteAnhydrite", "Apatite", "Azurite", "Biotite", "Calcite", "Chamosite", "Corundum", "Ferrohornblende", "Gypsum", "Hematite", "Kaolinite", "Microcline", "Montmorillonite", "Muscovite", "Pyrite", "Quartz", "Rutile", "Talc", "Zircon"]

twoT, diff = Conductor.openXRD(os.path.join(datafilepath, datafilename))
plot, results = Conductor.Qanalyze(twoT, diff ,difdata, phaselist, selectedphases, Lambda, Target)


#print plot, results

print "time of computation = %.2fs" %(time.time()-t0)