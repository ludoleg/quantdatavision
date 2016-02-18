import globals

import logging
import phaseanalyze as QUANT
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

import StringIO

# import io
# from PIL import Image

# This datastore model keeps track of which users uploaded which photos.
class UserData(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    phaselist = ndb.PickleProperty()
    avatar = ndb.BlobProperty()

def GenerateChart(obj_key):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    
    logging.info("Start with processing...")
    ludo = obj_key.get()
    logging.debug(ludo)
    blob_reader = blobstore.BlobReader(ludo.blob_key)
    
    XRDdata = blob_reader #file handle - not the name of the file

    phaselistname = "AutMin-phaselist-final.csv"
    phaselist = open(phaselistname, 'r').readlines()
    DBname = "Final_AutMin-Database-difdata.txt"
    difdata = open(DBname, 'r').readlines()

    # logging.debug(phaselist)
        
    # rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    # if globals.OSX:
    #     results = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    # else:
    #     results, rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)

    results, rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)

    rv_plot = StringIO.StringIO()
    
    ludo.phaselist = results
    output = rv_plot.getvalue()

    ludo.avatar = output
    ludo.put()
    
    logging.debug(ludo)
    logging.info("Done with processing")

    return results
    
#    if globals.OSX:
   #     return results
 #   else:
  #      return rv_plot
    
    # return results, rv_plot
    # return results



