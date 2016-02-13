import StringIO
import logging
import phaseanalyze as QUANT

def GenerateChart(blobfile):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    rv_plot = StringIO.StringIO()
    
    logging.info("Start with processing...")
    
    XRDdata = blobfile #file handle - not the name of the file
    difdata = "Final_AutMin-Database-difdata.txt"
    phaselist = "AutMin-phaselist-final.csv"

    logging.info("Done with processing")

    results, rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    
    return rv_plot
