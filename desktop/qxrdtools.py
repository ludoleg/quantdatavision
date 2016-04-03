# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 16:03:16 2014

@author: philippe
"""

from scipy.optimize import leastsq
import numpy as np
from math import *
import logging
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#from numba import jit

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

    return angle, diff #, target, Lambda  needs to be coded in txt and plv

    
def extractlists(phaselist) :
    '''
    #### extracts 3 lists: mineral, RIR, enable 
    '''
    mineral=[]
    RIR=[]
    enable=[]
    for i in range(1, len(phaselist)):
        line = phaselist[i]
        # logging.warning('%s before you %s', 'Look', 'leap!')
        # logging.debug(line)
        line = line[0:len(line)-1]
        phaselist[i] = line.split('\t')
        mineral.append(phaselist[i][0])
        RIR.append(float(phaselist[i][1]))
        enable.append(int(phaselist[i][2]))    
    return mineral, RIR, enable

'''
Bellow is the function to calculate the gaussian patterns using an erf function instead of a gaussian, to avoid sampling errors. 
It works but it's incredibly slow.   (65.s vs 1.5s).   Saved for later use:
if we detect 2theta sampling conditions not meeting Nyquist rule.
if max(FWHM) <2* 2theta_step (2theta_step =(X[len(X)-1]-X[0])/(len(X)-1)) then use gausspeakerf in place of gausspeak.

def phi(x):
    #Cumulative distribution function for the standard normal distribution
    #used to calculate the integral of the gaussian distribution inside a 2Theta bin
    phi=(1.0 + erf(x / sqrt(2.0))) / 2.0
    return phi
    
def gausspeakerf(X,X0,S):
    #X = 2T array, X0+peak position, S=sigma
    #calculates peak profile using Phi(x) function
    step = (X[len(X)-1]-X[0])/(len(X)-1)
    I = np.zeros_like(X)
    for i in range(0, len(X)-1):
        I[i] = phi((X[i]-X0+step/2)/S) - phi((X[i]-X0-step/2)/S)        
    return I
'''

def gausspeak(X,X0,S):
    #X = 2Theta array, X0+peak position, S=sigma
    #calculates peak profile using gauss function
    I = (1/S/sqrt(2*pi)) * e**(-(X-X0)**2/2/S**2)    
    return I
    
def gausspat (X,twoT, Irel, RIR, a, b):
    Yg = np.zeros_like(X)
    X = np.array(X)
    for i in range(0, len(twoT)):
        S = a * twoT[i] + b         
        Yg += Irel[i]*gausspeak(X, twoT[i], S)
    Yg *= RIR
    return Yg


def calculatePatDB(X,DB2T, DBInt, mineral, RIR, enable, a, b):
    '''
    calculates array of patterns
    '''
    PatDB = np.zeros((len(mineral),len(X)))
    for i in range(0, len(mineral)):
        if enable[i]==1:
            PatDB[i] = gausspat(X,DB2T[i], DBInt[i], RIR[i], a, b)
            if sum(PatDB[i])<10:  # this is to disable phases with no peaks in the angular range
                enable[i]=0
    return PatDB, enable


def sumPat(I, PatDB):
    '''
    computes the sum of patterns with I as intensity vector
    take PatDB 2D array and I 1D array
    '''
    PatDB = np.array(PatDB)    
    sumPat = np.zeros(PatDB.shape[1])
    for i in range(0,PatDB.shape[0]):
        sumPat+= I[i]*PatDB[i]
    return sumPat

    
def BGfit(angle, diff, BGsmoothing, w, w2, Polyorder):
    '''
    ####################   fits background   ###########################
    # Smoothing option
    #  BGsmoothing = boolean
    #  w = window width for minimum testing (INT)
    #  w2 = window width for averaging (INT)
    #  Polyorder= polynomial fit order (INT)
    '''
    if BGsmoothing:
        BGthresh = 1.25  
    else: 
        BGthresh = 1.5

    #########   Spot selection   ########################################
    diffBG = np.zeros_like(diff)
    BGX = []
    BGY = []

    if BGsmoothing:
        for i in range(0,len(angle)):
            minBGsmooth = max(i-w2/2, w2/2)
            maxBGsmooth = min(i+w2/2, len(angle)-w2/2)
            diffBG[i] = np.mean(diff[minBGsmooth:maxBGsmooth])
        else: 
            diffBG = diff

    for i in range(1,len(angle)-1):
        minBGwin = max(i-w/2, w/2)
        maxBGwin = min(i+w/2, len(angle)-w/2)
        if diffBG[i] < (min(diffBG[minBGwin:maxBGwin])*BGthresh):
            BGX.append(angle[i])
            BGY.append(diffBG[i])
    #########   Polynomial fit   ########################################
    if len(BGY)<10:
        BGpoly = diff-diff
    else:
        polycoefs = []
        polycoefs = np.polyfit(BGX,BGY,Polyorder)
        BGpoly = np.zeros(len(angle))
        for i in range(0, Polyorder+1):
            BGpoly += polycoefs[i] * angle ** (Polyorder-i)
    
    return BGpoly


def getLambdafromTarget(Target):
    if Target == "Cu":
        Lambda = 1.541838
    elif Target == 'Co':
        Lambda = 1.78897
    else : logging.info( 'ERROR: Tube target material unknown')
    return Lambda


def makeDB(difdata, mineral, enable, Lambda):
    """"
    # DB is a 3D list containing all data of each mineral
    ##  1st dimension:  mineral number
    ##  2nd dimension: peak number
    ##  3rd dimension: data 2T I d H K L Multiplicity
    """    
    
    limits_nameorder = []
    nameline = True
    name = []
    # loop bellow find the line positions of each beginning and end of difdata.txt
    for i in range(0, len(difdata)):
        line = difdata[i]
        if nameline:
            namelinenum = i
            name.append((line[6:len(line)-1]))
            nameline = False
        if "_END_" in line:
            endline = i
            limits_nameorder.append([namelinenum,endline])
            nameline = True

    limits = np.zeros_like(limits_nameorder)        
        
    for i in range(0,len(mineral)):
        for j in range(0,len(name)):
            if name[j] == mineral[i]:
                limits[i] = limits_nameorder[j]

    RIRcalc = []
    cellparam = []
    DB = np.zeros((len(mineral), 200, 7))
    peakcount = 0


    for i in range(0, len(mineral)):
        iv2=0
        Vcell=0
        datavalues = []
        peaknum = 0
        start = 99999
        if enable[i] == 1:
            for j in range (limits[i][0], limits[i][1]-3):
                line = difdata[j]
                if ("MAX. ABS. INTENSITY / VOLUME**2:") in line:
                    iv2=float(line[44:len(line)-1])
                    start=j+2
                elif ("CELL PARAMETERS:") in line:
                    cellparamline = line[24:len(line)-1]
                    cellparam = [float(n) for n in cellparamline.split()]
                    for k in range(3,6):
                        cellparam[k] *=pi/180
                    Vcell = cellparam[0] * cellparam[1] *cellparam[2] * (1- (cos(cellparam[3]))**2 - (cos(cellparam[4]))**2 - (cos(cellparam[5]))**2 + 2 * cos(cellparam[3]) * cos(cellparam[4]) * cos(cellparam[5]))**0.5
                elif j >= start and peaknum < 20:
                    linedata = difdata[j]   #       linedata = linedata[16:len(linedata)]
                    datavalues = [float(n) for n in linedata.split()]
                    if len(datavalues)==7:
                        #datavalues contains data in difdata card: 2T I d H K L Multiplicity
                        ##  recalculate 2t positions depending on Lambda  
                        datavalues[0] = 2*180/pi*asin(Lambda/2/datavalues[2])
                        if datavalues[0] >= 5 and datavalues[0] <= 55 :
                            DB[i][peaknum] = datavalues
                            peaknum += 1
            peakcount += peaknum + 1
            if iv2 > 0 and Vcell > 0:
                Imax = (iv2*Vcell)/3978.77*4
                RIRcalc.append(Imax)
            else:
                RIRcalc.append(0)

    return DB, RIRcalc, peakcount
#######################################################################################################################


def scalePat(X, Yexp, Pat, OStarget):
    """
    #  Scales pattern intensity using PatDB for initialization
    """
    tol = .5
    I = 1.

    Pat_area = sum(Pat)
    negativearea = 0

    for i in range(0, len(X)):
        if Yexp[i] < 0:
            negativearea += abs(Yexp[i])
            tol = 0.8  # tolerance factor on overshoot target
    ontarget = False
    if Pat_area <= 0 :
        ontarget = True
        I = 0 
    while ontarget==False:
        
        difference = Yexp - Pat*I
        negativearea2 = 0
        for i in range(0, len(X)):
            if difference[i] < 0:
                negativearea2 += abs(difference[i])      
        overshoot = (negativearea2-negativearea)/Pat_area
        if overshoot < OStarget*tol:
            I *= 1.2
        elif overshoot > OStarget/tol:
            I /= 1.2999
        else:
            ontarget = True
    return I


def getIinitPatDB(angle,diff,BGpoly,PatDB, mineral, enable, INIsmoothing, OStarget):
    """
    #######################   Initialization   ###################################
    ############   Computes mineral intensity sustained under diffractogram   ####
    ####   builds 1D array of intensity factors 
    ####  OStarget = overshoot of integral intensity of the single mineral (proportion of mineral calculated pattern above experimental data)
    ####allows removing phase that are obviously not present using Thresh 1D array
    """    
    
    
    Iinit = np.zeros(len(mineral))
    diffsmooth = np.zeros_like(diff)
    if INIsmoothing:
        w3 = 4  #width of smooothing window
        for i in range(0,len(angle)):
            minsmooth = max(i-w3/2, w3/2)
            maxsmooth = min(i+w3/2, len(angle)-w3/2)
            diffsmooth[i] = np.mean(diff[minsmooth:maxsmooth])  #computes smoothed value for i
    
    for i in range(0, len(mineral)):
        if  enable[i] == 1:
            Iinit[i] = scalePat(angle, (diff-BGpoly),PatDB[i],OStarget)
        else :
            Iinit[i] = 0
    return Iinit


def Ithresholding(mineral, enable,RIR, Ithreshratio, I):
    '''
    ####  turns minerals OFF (enable =0) if under their threshold%   ##############
    '''
    for i in range(0, len(enable)):        
        if enable[i]<>0 and  I[i] < max(I)*Ithreshratio:
            enable[i] = 0
            #logging.info("%s- init : %.4f >>> eliminated\t" %(mineral[i],I[i]))
    return enable


def Qthresholding(mineral, enable, Thresh, I):
    '''
    ####  turns minerals OFF (enable =0) if under their threshold%   ##############
    '''
    Q = I*enable/sum(I)*100
    
    for i in range(0, len(enable)):        
        if enable[i]<>0 and  Q[i] < Thresh[i]:
            enable[i] = 0
            #logging.info( "%s- init : %.1f >>> eliminated\t" %(mineral[i],Q[i]))
    return enable

def CleanMineralListPatDB (mineral, RIR, enable, Thresh, I, PatDB):
    '''
    #####  removes minerals in list if enable=0
    #####  restructures all lists in input
    #t0=time.time()
    '''
    mineralthresh = []
    RIRthresh=[]
    enablethresh=[]
    Threshthresh=[]
    Ithresh=[]
    PatDBthresh=[]
    
    for i in range(0, len(mineral)):
        if enable[i] == 1:
            mineralthresh.append(mineral[i])
            RIRthresh.append(RIR[i])
            enablethresh.append(enable[i])
            Threshthresh.append(Thresh[i])
            Ithresh.append(I[i])
            PatDBthresh.append(PatDB[i])
    #logging.info("list cleanup computing time = %.2f" %(time.time()-t0))
    return mineralthresh, RIRthresh, enablethresh, Threshthresh, Ithresh, PatDBthresh


def getKey(item):
    # used for sorting % results in decreasing order
    return item[4]


def sortQlistPatDB(mineral, RIR, enable, Thresh, I, PatDB):
    
    #######################   sorts lists in decreasing Q order      ############
    table = []
    for i in range(0,len(mineral)):
        table.append([mineral[i], RIR[i], enable[i], Thresh[i], I[i], PatDB[i]])

    table.sort(key=getKey, reverse=True)
    
    mineralsorted =[]
    enablesorted=[]
    RIRsorted=[]
    Threshsorted=[]
    Isorted=[]
    PatDBsorted=[]
    
    for i in range(0,len(mineral)):
        mineralsorted.append(table [i][0])
        RIRsorted.append(table[i][1])
        enablesorted.append(table[i][2])
        Threshsorted.append(table[i][3])
        Isorted.append(table[i][4])
        PatDBsorted.append(table[i][5])
    
    return mineralsorted, RIRsorted, enablesorted, Threshsorted, Isorted, PatDBsorted    
    
def residualPatDB(I, Yexp, PatDB):
    """
    # Residual function for least square optimization of gaussian peaks 
    #  variable to refine:  I = intensity factors list  
    """
    I = abs(I)
    return (Yexp-sumPat(I, PatDB))


def QrefinelstsqPatDB(angle,diff,BGpoly, mineral, RIR, enable, Thresh, Iinit, PatDB):
    """
    This function refine the % values of the mineral in the mixture using least-square optimization method.
    Requires scipy
    """
    Keep_refining = True
    counter = 0 # counts iteration of the refinement.
    I = abs(np.array(Iinit))
    precision=[0.1, 0.05, 0.01]

    while Keep_refining:
        ## recalculate DB with current list
        counter +=1
        t0=time.time()
        logging.info( "counter = %s     minerals:%s", counter, sum(enable))
        Keep_refining = False
        Istart = I
            
        I, tossme = leastsq(residualPatDB, Istart, args=(diff-BGpoly, PatDB),  gtol=precision[counter-1])#, col_deriv=1, maxfev=100)
        I=abs(I)       
        logging.info( "end LSTSQ #%s",  counter)

        enable2 = Qthresholding(mineral, enable, Thresh, I)
        #I *= enable2
        
        if sum(enable2) < sum(enable):
            Keep_refining = True
            enable = enable2
            mineral, RIR, enable, Thresh, I, PatDB = CleanMineralListPatDB(mineral, RIR, enable, Thresh, I, PatDB)
        
        if counter < 3:
            Keep_refining = True

        logging.info( "lstsq computing time =%s", (time.time()-t0))
        
    return mineral, RIR, enable, Thresh, I, PatDB 
