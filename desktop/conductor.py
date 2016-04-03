import logging
import numpy as np
from qxrdtools import *
import time

'''
code was modified to enable selectedphase list to be used.  QXRDtools remains unchanged.

'''

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
   
    # Initialization
    INIsmoothing = False
    OStarget = 0.01

    return(BGsmoothing,w,w2,Polyorder,addBG,INIsmoothing,OStarget)


def activatephases(mineral, enable, selectedphases):
    '''  
    This function activates phases by modifying the enable list based on a selected file files
    To be used with web-ap phase selection tool
    '''
    for i in range(0, len(mineral)):
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

def Qanalyze(angle, diff, difdata, phaselist, selectedphases, Lambda, Target, FWHMa, FWHMb):
    """
    This function orchestrates the quantitative analysis
    All critical functions are imported from QRDtools
    Use this to change the sequence of processing
    """

    logging.debug("Start Qanalyze")
    
    if Lambda in ('',0) and Target in ["Co", "Cu"]:
        Lambda = getLambdafromTarget(Target)
    if Lambda in ('',0) and Target == '':
        Target = "Co"
        Lambda = getLambdafromTarget(Target)
        logging.info('No Lambda or Target data:  assumed to be Co Ka')
    
    sigmaa = FWHMa / (2*sqrt(2*log(2)))
    sigmab = FWHMb / (2*sqrt(2*log(2)))
    #########    Process Background     #######################################
    
    BGsmoothing,w,w2,Polyorder,addBG,INIsmoothing,OStarget = Setparameters()

    BGpoly = BGfit(angle, diff, BGsmoothing, w, w2, Polyorder)

    # logging.debug('Starting PhaseAnalysis')
    # logging.debug(phaselist)
    
    ##########  Open minerals lists   #########################################

    mineral, RIR, enable = extractlists(phaselist)
    enable = activatephases(mineral, enable,selectedphases)
    
    #######################   Extract from difdata      ############
    
    logging.info("Starting extracting from difdata")
    starttime = time.time()
    DB, RIRcalc, peakcount = makeDB(difdata, mineral, enable, Lambda)
    DB2T = DB[:,:,0]
    DBInt = DB[:,:,1]
    PatDB, enable = calculatePatDB(angle,DB2T, DBInt, mineral, RIR, enable, sigmaa, sigmab)
    
    #print "Completed calculatePatDB, shape:",PatDB.shape
    logging.info("PatDB computing time = %.3fs" %(time.time()-starttime))
    Thresh = setQthresh(RIR)
    trashme = RIR
    mineral, RIR, enable, Thresh, trashme, PatDB = CleanMineralListPatDB (mineral, RIR, enable, Thresh, trashme, PatDB)
    
    initialize = True
    optimize = True
    
    starttime = time.time()
    if initialize:
        #print "number of mineral before initialization: ",sum(enable)
        logging.info("Start Initialization")
        Iinit = getIinitPatDB(angle,diff,BGpoly,PatDB, mineral,enable, INIsmoothing, OStarget)
        '''for i in range (0, len(mineral)):
            if enable[i]>0:
                print mineral[i], "=", Iinit[i]
        '''
        Ithresh = 0.05        
        enable = Ithresholding(mineral, enable,RIR, Ithresh, Iinit)
        while sum(enable) > 25:
            Ithresh += 0.01
            enable = Ithresholding(mineral, enable,RIR, Ithresh, Iinit)
            #print "Ithresh = ", Ithresh, "   minerals: ", sum(enable)
                    
        
        logging.info("Done computing Initialization")
       
        #####     remove minerals disabled by initialization       ################     
        mineral, RIR, enable, Thresh, Iinit, PatDB = CleanMineralListPatDB (mineral, RIR, enable, Thresh, Iinit, PatDB)

        #print "number of mineral after initialization: ", sum(enable)

        
    else:
        Iinit = np.array(([1.] * len(enable)))* np.array(enable)


    Sum_init = sumPat(Iinit, PatDB)
    #Sum_init *= max(diff-BGpoly)/max(Sum_init)
    Sum_init += BGpoly
    Qinit = Iinit/sum(Iinit)*100
    logging.info( "Iinit computing time = %.3fs" %(time.time()-starttime))
    
    for i in range(0,len(mineral)):
        logging.info("Qinit_%s : %.2f " %(mineral[i], Qinit[i]))
    
    #print "Phases enabled before optimize = ", sum(enable)
    starttime = time.time()
    if optimize:
        
        logging.info("Start computing optimization")
        
        mineral, RIR, enable, Thresh, I, PatDB = QrefinelstsqPatDB(angle, diff, BGpoly, mineral, RIR, enable, Thresh, Iinit, PatDB)
        
        logging.info("Done computing optimization- starting drawing")
    else:
        I = Iinit
    logging.info("Phases enabled = %.0f", sum(enable))
    logging.debug("Done phaseanalyze")
    #####  reorganize results by decreasing % order #########
    mineral, RIR, enable, Thresh, I, PatDB = CleanMineralListPatDB(mineral, RIR, enable, Thresh, I, PatDB)
    mineral, RIR, enable, Thresh, I, PatDB = sortQlistPatDB(mineral, RIR, enable, Thresh, I, PatDB)
    ####    #redo DB with shorter list    #####

    Sum= sumPat(I, PatDB)
    #Sum *= max(diff-BGpoly)/max(Sum)
    Sum += BGpoly
    
    for i in range (0, len(mineral)):
        logging.info("%s = %.2f" %(mineral[i], I[i]))
    
    Q = I/sum(I)*100
    logging.info("I Lstsq computing time = %.3fs" %(time.time()-starttime))
    logging.debug(mineral)
    
    '''for i in range(0,len(mineral)):
        logging.info("Q_%s : %.2f " %(mineral[i], Q[i]))
    '''
    results = []    
    for i in range(0, len(mineral)):
        results.append([mineral[i], '%.2f' %Q[i]])

    return results, BGpoly, Sum