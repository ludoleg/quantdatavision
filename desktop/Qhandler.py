# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""

import QXRDconductor
import numpy as np
import os
#from Tkinter import *
#from tkFileDialog import askopenfilename


datafilepath='/Users/ludo/Documents/workspace/autoquantplayground/XRD_data/'
datafilename = "Mix3B-film.txt"
DBfilepath=''
DBname="reduced_difdata.txt"
phaselistname = 'phaselist.csv'
Lambda = ''
Target = ''


#datafilepath, datafilename = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open XRD .txt file"))

#Tk().withdraw()

difdata = open((os.path.join(DBfilepath, DBname)), 'r').readlines()
phaselist = open(os.path.join(DBfilepath, phaselistname), 'r').readlines()
twoT, diff = QXRDconductor.openXRD(os.path.join(datafilepath, datafilename))
plot = QXRDconductor.Qanalyze(twoT, diff ,difdata, phaselist, Lambda, Target)

print plot
