# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 16:03:16 2014

@author: philippe
"""
import logging
import numpy as np

def openXRD(file, filename):
    """
   Opens an XRD file and returns two 1D array for 2theta and Intensity
   possible formats: TXT, PLV, DIF, MDI   ....   more to come
    """
    logging.debug("Starting openXRD")
    blob = open(file, 'r')
    
    if filename.endswith(".plv"): 
        jump=50
        XRDdata = blob.readlines()[jump:]
        # XRDdata = blob.open().readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
       
    elif filename.endswith(".txt"):
        txtfile = blob.readlines()
        # XRDdata = blob.open().readlines()[jump:]
        jump = 0
        i=0
        while txtfile[i].startswith('#'):
            jump+=1
            i+=1
        angle, diff = np.loadtxt(txtfile[jump:], unpack=True, delimiter='\t')

    elif filename.endswith(".dif") or filename.endswith(".mdi"):
        dif = blob.readlines()
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
             
    elif filename.endswith(".csv"):
         csvfile = blob.readlines()
         # XRDdata = blob.open().readlines()[jump:]
         jump = 0
         i=0
         while csvfile[i].startswith('#'):
             jump+=1
             i+=1
         angle, diff = np.loadtxt(csvfile[jump:], unpack=True, delimiter=',')

    else:     
        logging.debug("file format error: plv, txt, dif, mdi required.")
   
    return (angle, diff)

