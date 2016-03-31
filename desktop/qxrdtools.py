# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 16:03:16 2014

@author: philippe
"""

from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt
from math import *
import logging

from numba import jit

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
        #print lastline
        for i in range(0,len(lastline)):
             diffindex = ((len(dif)-3)*8)+i
             diff[diffindex]=float(lastline[i])
    '''else:     
        print "file format error: plv, txt, dif, mdi required."
    '''    
    return angle, diff #, target, Lambda  needs to be coded in txt and plv

#############################################################################################


    
def extractlists(phaselist) :
    ######### extracts 3 lists: mineral, RIR, enable #############################
    
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
    


def scalepattern(X, Yexp, DB2T, DBInt, RIR, a, b, OStarget):
    """
    #   used to initialize a mineral intensity
    #  OStarget = overshoot target ratio, corresponds to the proportion of 
    #  integral intensity of the mineral that shoots over the experimaental data
    """
    tol = .5
    I = 1.
    if RIR > 0:
        Yg = np.zeros_like(X)
        for i in range(0, len(DB2T)):
            S = a * DB2T[i] + b
            Yg += (DBInt[i]*RIR/S/sqrt(2*pi)) * e**(-(X-DB2T[i])**2/2/S**2)

        Gauss_area = sum(Yg)
        negativearea = 0
    
        for i in range(0, len(X)):
            if Yexp[i] < 0:
                negativearea += abs(Yexp[i])
                tol = 0.8  # tolerance factor on overshoot target
        ontarget = False
        if Gauss_area <= 0 :
            ontarget = True
            I = 0
            
    while ontarget==False:
        
        difference = Yexp - Yg*I
        negativearea2 = 0        
        for i in range(0, len(X)):
            if difference[i] < 0:
                negativearea2 += abs(difference[i])      
        overshoot = (negativearea2-negativearea)/Gauss_area
        if overshoot < OStarget*tol:
            I *= 1.2
        elif overshoot > OStarget/tol:
            I /= 1.3
        else:
            ontarget = True
    
    return I

       
    
def BGfit(angle, diff, BGsmoothing, w, w2, Polyorder):
    ####################   fits background   ###########################
    # Smoothing option
    #  BGsmoothing = boolean
    #  w = window width for minimum testing (INT)
    #  w2 = window width for averaging (INT)
    #  Polyorder= polynomial fit order (INT)

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
        #print "too few background points selected"
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
    #else : print 'ERROR: Tube target material unknown'
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
                    #print "a=%.2f, b=%.2f, c=%.2f" % (cellparam[0], cellparam[1], cellparam[2])               
                    #print "alpha=%.2f, beta=%.2f, Gamma=%.2f" % (cellparam[3], cellparam[4], cellparam[5])                    
                    #print Vcell
                elif j >= start and peaknum < 20:
                    linedata = difdata[j]   #       linedata = linedata[16:len(linedata)]
                    datavalues = [float(n) for n in linedata.split()]
                    if len(datavalues)==7:
                        #print datavalues
                        #datavalues contains data in difdata card: 2T I d H K L Multiplicity
                        ##  recalculate 2t positions depending on Lambda  
                        datavalues[0] = 2*180/pi*asin(Lambda/2/datavalues[2])
                        if datavalues[0] >= 5 and datavalues[0] <= 55 :
                            DB[i][peaknum] = datavalues
                            peaknum += 1
            peakcount += peaknum + 1
            if iv2 > 0 and Vcell > 0:
                Imax = (iv2*Vcell)/3978.77*4
                #print mineral[i] + "  : Imax =%.2f" % Imax
                RIRcalc.append(Imax)
            else:
                RIRcalc.append(0)

    return DB, RIRcalc, peakcount
#######################################################################################################################

def getIinit(angle,diff,BGpoly,DB2T, DBInt, mineral, RIR, enable, INIsmoothing, OStarget,a,b):
    """
    #######################   Initialization   ###################################
    ############   Computes mineral intensity sustained under diffractogram   ####
    ####   builds 1D array of intensity factors 
    ####  OStarget = overshoot of integral intensity of the single mineral (proportion of mineral calculated pattern above experimental data)
    ####allows removing phase that are obviously not present using Thresh 1D array
    """    
    
    
    Iinit = np.zeros_like(RIR)
    diffsmooth = np.zeros_like(diff)
    
    if INIsmoothing:
        w3 = 4  #width of smooothing window
        for i in range(0,len(angle)):
            minsmooth = max(i-w3/2, w3/2)
            maxsmooth = min(i+w3/2, len(angle)-w3/2)
            diffsmooth[i] = np.mean(diff[minsmooth:maxsmooth])  #computes smoothed value for i
    
    for i in range(0, len(mineral)):
        if RIR[i] > 0 and enable[i] >0:
            #print "RIR(" + mineral[i] + ')= %.1f' %RIR[i]
            Iinit[i] = scalepattern(angle, (diff-BGpoly), DB2T[i], DBInt[i], RIR[i], a, b, OStarget)
            #print Iinit[i]
        else :
            Iinit[i] = 0
    return Iinit

def Ithresholding(mineral, enable,RIR, Ithreshratio, I):
    ####  turns minerals OFF (enable =0) if under their threshold%   ##############
    
    for i in range(0, len(enable)):        
        if enable[i]<>0 and  I[i] < max(I)*Ithreshratio:
            enable[i] = 0
            #print mineral[i], "- init : %.4f >>> eliminated\t" %I[i]  
    return enable


def Qthresholding(mineral, enable, Thresh, I):
    ####  turns minerals OFF (enable =0) if under their threshold%   ##############
    Q = I*enable/sum(I)*100
    
    for i in range(0, len(enable)):        
        if enable[i]<>0 and  Q[i] < Thresh[i]:
            enable[i] = 0
            #print mineral[i], "- init : %.1f >>> eliminated\t" %Qinit[i]  
    return enable


def CleanMineralList (mineral, RIR, enable, Thresh, I):
    #####  removes minerals in list if enable=0
    #####  restructures all lists in input
    mineralthresh = []
    RIRthresh=[]
    enablethresh=[]
    Threshthresh=[]
    Ithresh=[]
    
    for i in range(0, len(mineral)):
        if enable[i] == 1:
            mineralthresh.append(mineral[i])
            RIRthresh.append(RIR[i])
            enablethresh.append(enable[i])
            Threshthresh.append(Thresh[i])
            Ithresh.append(I[i])
            
    return mineralthresh, RIRthresh, enablethresh, Threshthresh, Ithresh


def getKey(item):
    # used for sorting % results in decreasing order
    return item[4]
    
    
def sortQlist(mineral, RIR, enable, Thresh, I):
    
    #######################   sorts lists in decreasing Q order      ############
    table = []
    for i in range(0,len(mineral)):
        table.append([mineral[i], RIR[i], enable[i], Thresh[i], I[i]])

    table.sort(key=getKey, reverse=True)
    
    mineralsorted =[]
    enablesorted=[]
    RIRsorted=[]
    Threshsorted=[]
    Isorted=[]
    
    for i in range(0,len(mineral)):
        mineralsorted.append(table [i][0])
        RIRsorted.append(table[i][1])
        enablesorted.append(table[i][2])
        Threshsorted.append(table[i][3])
        Isorted.append(table[i][4])
    
    return mineralsorted, RIRsorted, enablesorted, Threshsorted, Isorted
    
def makeparam(mineral, RIR, enable, DB2T, DBInt, a, b, addBG):
    """
    calculate parameter list for functions
    ############################
    #   param:  
    #   0 = a sigma
    #   1 = b sigma
    #   2 = addBG
    #   3 = 
    #   10 = start RIR vector
    #   1000 = start index DB2T mineral 1 (step2)
    #   1001 = start index DBInt mineral 1 (step2)
    #   2000 = start index DB2T mineral 2 (step2)
    #   2001 = start index DBInt mineral 2 (step2)
    #   .....etc
    ###############################
    """

    param = [0]*(1000*2*(len(mineral)+1))
    param[0]= a
    param[1] = b
    for i in range(0, len(mineral)):
        param[i+10] = RIR[i]*enable[i]
        for j in range(0, DB2T.shape[1]/2):
            param[(1+i)*1000 + 2*j] = DB2T[i,j]
            param[(1+i)*1000 + 2*j+1] = DBInt[i,j] 
    return param   


def gausspat (I, X, param):
##  uses same parameter convention as "residual"
#
    Yg = np.zeros_like(X)
    X = np.array(X)
    for i in range(0, len(I)):  #index scanning all phases
        RIR = param[i+10]
        j=(i+1)*1000
        while param[j] > 0 and RIR > 0:
            DB2T = param[j]
            Irel = param[j+1]
            S = param[0]*DB2T + param[1]   #S=sigma
            # Yg += I[i]*Irel*RIR/S/sqrt(2*pi) * e**(-(X-DB2T)**2/2/S**2)
            Yg += I[i]*Irel*RIR/S/2.5 * e**(-(X-DB2T)**2/2/S**2)
            j += 2
    return Yg

def residual(I, X, Yexp, param):
    """
    # Residual function for least square optimization of gaussian peaks 
    #  variable to refine:  I = intensity factors list  
    #  param as definded in makeparam function
    """
    I = abs(I)
    Yg = gausspat(I,X,param)
    if param[2] > 0:  #this line adds a refined constant background
        Yg = Yg + I[len(I)-1]

    #print "integral error = %.2f" % (sum(abs(Yexp-Yg))/len(Yexp))

    return (Yexp-Yg)
   
def Qrefinelstsq(angle,diff,BGpoly,DB2T, DBInt, mineral, RIR, enable, Thresh, Iinit, a, b, Lambda, addBG):
    """
    This function refine the % values of the mineral in the mixture using least-square optimization method.
    Requires scipy
    """
    Keep_refining = True
    counter = 0 # counts iteration of the refinement.
    I = abs(np.array(Iinit))
    precision=[0.1, 0.01, 0.01]

    while Keep_refining:
        ## recalculate DB with current list
        counter +=1
        #print "counter = ", counter, '     minerals:', sum(enable)
        param = makeparam(mineral, RIR, enable, DB2T, DBInt, a, b, addBG)
        Keep_refining = False
        Istart = I
        if addBG<>0:
            Istart.append(addBG)
            param[2]=1
            
        I, tossme = leastsq(residual, Istart, args=(angle, diff-BGpoly, param),  gtol=precision[counter-1])#, col_deriv=1, maxfev=100)
        I=abs(I)        
        logging.info( "end LSTSQ #",  counter)
        #print "I result:", I
        # enable2 allows reducing the number of phases taken into account in the computation.
        enable2 = Qthresholding(mineral, enable, Thresh, I)
        I *= enable2
        
        if sum(enable2) < sum(enable):
            Keep_refining = True
            enable = enable2
        
        if counter < 3:
            Keep_refining = True
        '''if counter == 3:
            print "Step 3 results: "            
            for i in range (0, len(mineral)):
                    print mineral[i], "=",I[i]
        '''
        
    return I
