# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 14:35:37 2014

@author: philippe
"""
from Tkinter import *
from tkFileDialog import askopenfilename
import time
import os

diffpath,diffname = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open difdata.txt file"))
difdata = open((os.path.join(diffpath,diffname)), 'r').readlines()

CSVpath,CSVname = os.path.split(askopenfilename(filetypes=[("CSV files","*.csv")], title="Open phase selection list CSV file"))
listmin = open((os.path.join(CSVpath,CSVname)), 'r').readlines()

#############################################################################################################
###################################   Open Files   ###########################################################
#############################################################################################################

cardsassigned = []

for j in range(1, len(listmin)):
    line = listmin[j].split('\t')
    line[1] = int(line[1])
    if line[1]>0:
        cardsassigned.append(line[1])


### create/erase file to save selected difdata phases
creationtime=str(time.time())

open((os.path.join(diffpath,"difdata_%s.txt" %creationtime)),'w').close()
f = open((os.path.join(diffpath,"difdata_%s.txt" %creationtime )), 'a')


#############################################################################################################
###################################   process Diffdata   ####################################################
#############################################################################################################

phasefound = [0] * len(listmin)  # this list keeps track of what mineral found one or more matches in difdata
keepercounter =0
nameline = True #  this boolean is used to identify a mineral name line (1st ine or following a _end_ line)
linenum = 0
keeper = False   #  this boolean is used to keep or reject each difdata card

for i in range(0, len(difdata)):
    line = difdata[i]
    if nameline:
        nameline = False
        AMCSDnum = 0
        if i < (len(difdata)-11):
            for k in range(i+3, i+11):                 
                currentline = difdata[k]
                if currentline.startswith("      _database_code_amcsd "):
                    AMCSDnum = int(currentline[27:-1])
                
            if AMCSDnum == 0:
                print ('AMCSD ID not found')                

            if (AMCSDnum in  cardsassigned):
                print "%s found" % AMCSDnum
                keeper = True
                keepercounter += 1
           
         
    if keeper:
        f.write(difdata[i])                                          
    if '_END_' in line:
        nameline = True
        keeper = False
        
print "number of cards found: ", keepercounter
print "number of cards not found: ", len(cardsassigned)-keepercounter

f.close()
