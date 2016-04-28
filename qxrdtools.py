# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 16:03:16 2014

@author: philippe
"""
import logging
import numpy as np

def openXRD(blob, nomdufichier):
    """
   Opens an XRD file and returns two 1D array for 2theta and Intensity
   possible formats: TXT, PLV, DIF, MDI   ....   more to come
    """
    logging.debug("Starting openXRD")
    if nomdufichier.endswith(".plv"): 
        jump=50
        XRDdata = blob.readlines()[jump:]
        # XRDdata = blob.open().readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
       
    elif nomdufichier.endswith(".txt"):
        jump=7
        XRDdata = blob.readlines()[jump:]
        # XRDdata = blob.open().readlines()[jump:]
        angle, diff = np.loadtxt(XRDdata, unpack=True)
        
    elif nomdufichier.endswith(".dif") or nomdufichier.endswith(".mdi"):
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
        print lastline
        for i in range(0,len(lastline)):
             diffindex = ((len(dif)-3)*8)+i
             diff[diffindex]=float(lastline[i])
    else:     
        # print "file format error: plv, txt, dif, mdi required."
        logging.debug("file format error: plv, txt, dif, mdi required.")
        
    return angle, diff #, target, Lambda  needs to be coded in txt and plv
    
