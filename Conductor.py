import logging
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from QXRDtools import *
from math import *
import StringIO


'''
code was modified to enable selectedphase list to be used.  QXRDtools remains unchanged.

'''
# import io
# from PIL import Image

# Almost entirely generic
# Provides the logic for generating the plot and the CSV file data

# Input xxx.txt containing phase, angle
# DB, Phase list static
# Output Plot, list for CSV file generation



#if xxx = GAE then
#else


def Setparameters():
    """
    this function sets parameters for QXRD analysis.
    It also serves as a patch for the poor implementation of metadata reading from XRD files
    and for the current absence of user calibration tools (find a, b, possible 2theta offsets)
    Should eventually be replaced by parameters sent from handlers based on user settings
    """
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


def activatephases(mineral, enable, selectedphases):
    '''  
    This function activates phases by modifying the enable list based on a selected file files
    To be used with web-ap phase selection tool
    '''
    for i in range(1, len(mineral)):
        if mineral[i] in selectedphases:
            enable[i] = 1
        else:
            enable[i] = 0
    return enable


def setQthresh(RIR):
    #######################   Define Initialization Threshold list      ############
    Thresh = np.zeros_like(RIR)
    for i in range(0,len(RIR)):
        if RIR[i] < 1:
            Thresh[i] = 5.
        if RIR[i] >= 1:
            Thresh[i] = 3
        if RIR[i] >= 2:
            Thresh[i] = 2
    return Thresh

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
        plt.text(12, vertpos,"%.1f" %float(graphlist[i][1]), fontsize=12, color="blue")
        vertpos -= offset/15
    if len(graphlist) == 10:
        plt.text(6, vertpos,"...", fontsize=12, color="blue")

    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # buf.seek(0)
    # plot = Image.open(buf)
    # buf.close()
    # return plot

    plt.show
    
    ludo_rv = StringIO.StringIO()
    plt.savefig(ludo_rv, format="png")
    plt.clf()

    return ludo_rv

def Qanalyze(angle, diff, difdata, phaselist, selectedphases, Lambda, Target):
    """
    This function orchestrates the quantitative analysis
    All critical functions are imported from QRDtools
    Use this to change the sequence of processing
    """

    logging.debug("Start Qanalyze")
    
    if Lambda == '' and Target in ["Co", "Cu"]:
        Lambda = getLambdafromTarget(Target)
    if Lambda =='' and Target == '':
        Target = "Co"
        Lambda = getLambdafromTarget(Target)
        logging.info('No Lambda or Target data:  assumed to be Co Ka')
    
    #########    Process Background     #######################################
    
    BGsmoothing,w,w2,Polyorder,addBG,INIsmoothing,OStarget,a,b,Target = Setparameters()

    BGpoly = BGfit(angle, diff, BGsmoothing, w, w2, Polyorder)

    # logging.debug('Starting PhaseAnalysis')
    # logging.debug(phaselist)
    
    ##########  Open minerals lists   #########################################

    mineral, RIR, enable = extractlists(phaselist)
    enable = activatephases(mineral, enable,selectedphases)
    
    #######################   Extract from difdata      ############
    
    logging.info("Starting extracting from difdata")

    DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Lambda)
    DB2T = DB[:,:,0]
    DBInt = DB[:,:,1]
    
    Thresh = setQthresh(RIR)    

    initialize = True
    optimize = True
    
    
    if initialize:
        
        logging.info("Start Initialization")
        Iinit = getIinit(angle,diff,BGpoly,DB2T, DBInt, mineral, RIR, enable, INIsmoothing, OStarget, a, b)
        logging.info("Done computing Initialization")
       
        #####     remove minerals dsiabled by initializaation       ################     
        mineral, RIR, enable, Thresh, Iinit = CleanMineralList (mineral, RIR, enable, Thresh, Iinit)
        ####    #redo DB with shorter list    #####
        DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Lambda)
        DB2T = DB[:,:,0]
        DBInt = DB[:,:,1]
    
    else:
        Iinit = np.array(([1.] * len(enable)))* np.array(enable)
    
    param = makeparam(mineral, RIR, enable, DB2T, DBInt, a, b, False)
    
    Sum_init = gausspat(Iinit, angle, param)
    Sum_init *= max(diff-BGpoly)/max(Sum_init)
    Sum_init += BGpoly
    Qinit = Iinit/sum(Iinit)*100

    for i in range(0,len(mineral)):
        logging.info("Qinit_%s : %.2f " %(mineral[i], Qinit[i]))
    

    if optimize:
        
        logging.info("Start computing optimization")
        
        I = Qrefinelstsq(angle, diff, BGpoly, DB2T, DBInt, mineral, RIR, enable, Thresh, Iinit, a, b, Lambda, False)
        
        logging.info("Done computing optimization- starting drawing")
    else:
        I = Iinit
    
    logging.debug("Done phaseanalyze")
    #####  reorganize results by decreasing % order #########
    mineral, RIR, enable, Thresh, I = CleanMineralList(mineral, RIR, enable, Thresh, I)
    mineral, RIR, enable, Thresh, I = sortQlist(mineral, RIR, enable, Thresh, I)
    ####    #redo DB with shorter list    #####
    DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Lambda)
    DB2T = DB[:,:,0]
    DBInt = DB[:,:,1]
    param = makeparam(mineral, RIR, enable, DB2T, DBInt, a, b, False)
    
    Sum= gausspat(I, angle, param)
    Sum *= max(diff-BGpoly)/max(Sum)
    Sum += BGpoly
    Q = I/sum(I)*100

    logging.debug(mineral)
    
    for i in range(0,len(mineral)):
        logging.info("Q_%s : %.2f " %(mineral[i], Q[i]))
    
    results = []    
    for i in range(0, len(mineral)):
        results.append([mineral[i], Q[i]])    
    
    plot = overplotgraph(angle,diff,BGpoly,Sum, results[0:min(10,len(mineral))])
    return results, plot



