# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:36:53 2016

@author: philippe
"""
import numpy as np
import matplotlib.pyplot as plt
from math import *

# import io
# from PIL import Image

# Almost entirely generic
# Provides the logic for generating the plot and the CSV file data

# Input xxx.txt containing phase, angle
# DB, Phase list static
# Output Plot, list for CSV file generation


#if xxx = GAE then
#else

def PhaseAnalyze(XRDdata,difdata,phaselist):
    
    BGsmoothing,w,w2,Polyorder,addBG,INIsmoothing,OStarget,a,b,Target = Setparameters()
    angle, diff = np.loadtxt(XRDdata, unpack=True)
    BGpoly = BGfit(angle, diff, BGsmoothing, w, w2, Polyorder)


    ##########  Open minerals list   #############################################
    ######### extracts 3 lists: mineral, RIR, enable #############################

    mineral=[]
    RIR=[]
    enable=[]
    for i in range(1, len(phaselist)):
        line = phaselist[i]
        line = line[0:len(line)-1]
        phaselist[i] = line.split('\t')
        mineral.append(phaselist[i][0])
        RIR.append(float(phaselist[i][1]))
        enable.append(int(phaselist[i][2]))    
    
    #######################   Extract from difdata      ############
    
    DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Target)
    DB2T = DB[:,:,0]
    DBInt = DB[:,:,1]
    #print 'peakcount = ', peakcount
    
    Sum, results = Quantifyinit(angle,diff,BGpoly,DB2T, DBInt, mineral, RIR, enable, difdata, INIsmoothing,OStarget,a,b,Target)
    

    plot = overplotgraph(angle,diff,BGpoly,Sum, results[0:min(len(results), 10)])
    
    
    return results, plot

##############################################################################
#########################  FUNCTION DEFINITIONS #############################
##############################################################################
def Setparameters():
  
    BGsmoothing = True
    w = 100
    w2 = 4
    Polyorder = 4
    addBG = 0  # enter 0 to disable
    
    # broadening function parameters a.x+b
    a = -0.001348 / (2*sqrt(2*log(2)))
    b = 0.352021 / (2*sqrt(2*log(2)))
   
    # Initialization
    INIsmoothing = False
    OStarget = 0.01
    Target = "Co"
    return(BGsmoothing,w,w2,Polyorder,addBG,INIsmoothing,OStarget,a,b,Target)



def residual(I, X, Yexp, param):
# Residual function for least square optimization of gaussian peaks 
#  variable to refine:  I = intensity factors list  
#  param:  
#   0 = a sigma
#   1 = b sigma
#   2 = addBG
#   3 = 
#   10 = start RIR vector
#   1000 = start index DB2T mineral 1 (step2)
#   1001 = start index Int% mineral 1 (step2)
#   2000 = start index DB2T mineral 2 (step2)
#   2001 = start index Int% mineral 2 (step2)
#   .....etc
#
    Yg = np.zeros_like(Yexp)
    X = np.array(X)
    for i in range(0, len(I)-1):  #index scanning all phases
        RIR = param[i+10]
        j=(i+1)*1000
        while param[j] > 0 and RIR > 0:
            DB2T = param[j]
            Irel = param[j+1]
            S = param[0]*DB2T + param[1]   #S=sigma
            Yg += abs(I[i])*Irel*RIR/S/sqrt(2*pi) * e**(-(X-DB2T)**2/2/S**2)
            j += 2
    if param[2] > 0:  #this line adds a refined constant background
        Yg = Yg + I[len(I)-1]

    #print "integral error = %.2f" % (sum(abs(Yexp-Yg))/len(Yexp))

    return (Yexp-Yg)
    
    
    
    
def gausspat2 (I, X, param):
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
            Yg += I[i]*Irel*RIR/S/sqrt(2*pi) * e**(-(X-DB2T)**2/2/S**2)
            j += 2
    return Yg




def scalegaussmin(X, Yexp, DB2T, DBInt, RIR, a, b, OStarget):
#   used to initialize a mineral intensity
#  OStarget = overshoot target ratio, corresponds to the proportion of 
#  integral intensity of the mineral that shoots over the experimaental data
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




def makeDB(difdata, mineral, enable, Target):
# DB is a 3D list containing all data of each mineral
##  1st dimension:  mineral number
##  2nd dimension: peak number
##  3rd dimension: data 2T I d H K L Multiplicity
    limits_nameorder = []
    nameline = True
    name = []
    # loop bellow find the line positions of each beginning and end 
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
    if Target == "Cu":
        Lambda = 1.541838
    elif Target == 'Co':
        Lambda = 1.78897
    #else : print 'ERROR: Tube target material unknown'

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


def getKey(item):
    return item[1]

def Quantifyinit(angle,diff,BGpoly,DB2T, DBInt, mineral, RIR, enable, difdata, INIsmoothing,OStarget,a,b,Target):
    
    #######################   Define Initialization Threshold list      ############
    Thresh = np.zeros_like(RIR)
    for i in range(0,len(RIR)):
        if RIR[i] < 1:
            Thresh[i] = 1.
        if RIR[i] >= 1:
            Thresh[i] = .5
        if RIR[i] >= 2:
            Thresh[i] = .2
    
    #######################   Initialization   ###################################
    ############   Computes mineral intensity sustained under diffractogram   ####
    ####   builds 1D array of intensity factors 
    ####  OStarget = overshoot of integral intensity of the single mineral (proportion of mineral calculated pattern above experimental data)
    
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
            Iinit[i] = scalegaussmin(angle, (diff-BGpoly), DB2T[i], DBInt[i], RIR[i], a, b, OStarget)
            #print Iinit[i]
        else :
            Iinit[i] = 0
    
    Qinit = []
    Qinit = Iinit*enable/sum(Iinit)*100
    #print "Initialization:"
    for i in range(0, len(mineral)):        
        if enable[i]<>0:
            #print "Qinit(" + mineral[i] + ')= %.1f' %Qinit[i]
            if Qinit[i] < Thresh[i]:
                enable[i] = 0
                #print mineral[i], "- init : %.1f >>> eliminated\t" %Qinit[i]
            #else:
                #print mineral[i], "- init : %.1f" %Qinit[i]      
    
    mineralstart = mineral
    mineral=[]
    RIRstart=RIR
    RIR=[]
    enablestart=enable
    enable=[]
    Threshstart=Thresh
    Thresh=[]
    I=[]
    
    for i in range(0, len(mineralstart)):
        if enablestart[i] == 1:
            mineral.append(mineralstart[i])
            enable.append(enablestart[i])
            RIR.append(RIRstart[i])
            Thresh.append(Threshstart[i])
            I.append(Iinit[i])
    
    #######################   Define refinement Threshold list      ############
    
    Thresh = np.zeros_like(RIR)
    for i in range(0,len(RIR)):
        if RIR[i] < 1:
            Thresh[i] = 3.
        if RIR[i] >= 1:
            Thresh[i] = 2
        if RIR[i] >= 2:
            Thresh[i] = 1

    Q = I/sum(I)*100    
    for i in range(0,len(mineral)):
        if Q[i]<Thresh[i]:
            enable[i]=0
    
    mineral_buf = mineral
    enable_buf = enable
    RIR_buf = RIR
    Thresh_buf = Thresh
    I_buf = I
    mineral = []
    enable = []
    RIR = []
    Thresh = []
    I = []
    for i in range(0, len(mineral_buf)):
        if enable_buf[i] == 1:
            mineral.append(mineral_buf[i])
            enable.append(enable_buf[i])
            RIR.append(RIR_buf[i])
            Thresh.append(Thresh_buf[i])
            I.append(I_buf[i])
    #redo DB with shorter list
    DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Target)
    DB2T = DB[:,:,0]
    DBInt = DB[:,:,1]
    ## calculate parameter list for functions
    param = [0]*(1000*2*(len(mineral)+1))
    param[0]= a
    param[1] = b
    for i in range(0, len(mineral)):
        param[i+10] = RIR[i]*enable[i]
        for j in range(0, DB2T.shape[1]/2):
            param[(1+i)*1000 + 2*j] = DB2T[i,j]
            param[(1+i)*1000 + 2*j+1] = DBInt[i,j] 


    Q = I/sum(I)*100   
    Sum = gausspat2(I, angle, param)
    Sum *= max(diff-BGpoly)/max(Sum)
    Sum += BGpoly
    
    Qresults = []
    # makes sorted list of mineral, Q
    for i in range(0,len(mineral)):
        Qresults.append([mineral[i],Q[i]])

    Qresults.sort(key=getKey, reverse=True)    

    for i in range(0,len(Qresults)):
        print "%s : %.2f " %(Qresults[i][0], Qresults[i][1])


    return (Sum, Qresults)


def overplotgraph(angle,diff,BGpoly,Sum, graphlist):
    fig = plt.figure(figsize=(15,5)) 
    plt.plot(angle, diff, linestyle="none",  marker=".",  color="black")
    fig.patch.set_facecolor('white')
    plt.xlabel('2-theta (deg)')
    plt.ylabel('intensity')
    #plt.plot(BGX, BGY, linestyle="none",  marker="o", color="yellow")  #plots data og calculate linear background
    #plt.plot(angle, Diffmodel, linestyle="solid", color="green")
    plt.plot(angle, BGpoly, linestyle="solid", color="red")
    plt.plot(angle, Sum, linestyle="solid", color="green")
    plt.xlim(5,55)
    plt.ylim(0,max(diff)*2)
    
    offset = max(diff)/2*3
    difference_magnification = 1
    difference = (diff - Sum) * difference_magnification
    offsetline = [offset]*len(angle)
    plt.plot(angle, difference+offset, linestyle="solid", color="red")
    plt.plot(angle, offsetline, linestyle="solid", color="pink")
    
    FOM = sum(abs(diff-Sum))/len(diff)
    plt.text(6, offset/10*12, "FOM = %.2f" %(FOM), fontsize=12, color="red")
    vertpos = offset/10*9
    for i in range(0,len(graphlist)):
        plt.text(6, vertpos,"%s :" %graphlist[i][0], fontsize=12, color="blue")
        plt.text(18, vertpos,"%.1f" %float(graphlist[i][1]), fontsize=12, color="blue")
        vertpos -= offset/15

    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # buf.seek(0)
    # plot = Image.open(buf)
    # buf.close()
    # success = True
    # return plot

    plt.show()
    
    ludo_rv = StringIO.StringIO()
    plt.savefig(ludo_rv, format="png")
    plt.clf()

    return ludo_rv
