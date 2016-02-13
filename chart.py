import logging
import phaseanalyze as QUANT

def GenerateChart(blobfile):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
        
    logging.info("Start with processing...")
    
    XRDdata = blobfile #file handle - not the name of the file

    phaselistname = "AutMin-phaselist-final.csv"
    phaselist = open(phaselistname, 'r').readlines()
    DBname = "Final_AutMin-Database-difdata.txt"
    difdata = open(DBname, 'r').readlines()

    # logging.debug(phaselist)

    rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    # results = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    logging.info("Done with processing")
    
    return rv_plot
    # return results, rv_plot



