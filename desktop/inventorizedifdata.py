# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 16:03:16 2014

@author: philippe
"""

from Tkinter import *
from tkFileDialog import askopenfilename
#import sys

path,DBname = os.path.split(askopenfilename(filetypes=[("TXT files","*.txt")], title="Open difdata.txt file"))
difdata = open((os.path.join(path,DBname)), 'r').readlines()

listname = '%s_list.csv' %DBname
open((os.path.join(path,listname)),'w').close()
f = open(os.path.join(path,listname),'a')
f.write("name\tAMCSD_code\n")

nameline = True
name=''
code=''

for line in difdata:
    linestr = line.split('\r')[0].split('\n')[0]
    if nameline:
        name = linestr[6:]
        nameline = False
    if '_database_code_amcsd' in line:
        code = linestr[28:]
    
    if "_END_" in line:
        nameline = True
        f.write('%s\t%s\n' %(name,code))
        name=''
        code=''
f.close()