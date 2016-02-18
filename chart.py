import globals
import logging
import phaseanalyze as QUANT
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

import StringIO

# import io
from PIL import Image

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
    # logging.debug(ludo)
    blob_reader = blobstore.BlobReader(ludo.blob_key)
    
    XRDdata = blob_reader #file handle - not the name of the file

    phaselistname = "AutMin-phaselist-final.csv"
    phaselist = open(phaselistname, 'r').readlines()
    DBname = "Final_AutMin-Database-difdata.txt"
    difdata = open(DBname, 'r').readlines()

    if globals.OSX:
        results = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
        file = open("cristal.jpg")
        ludo.avatar = file.read()
    else:
        rv_plot = StringIO.StringIO()
        results, rv_plot = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
        rv_plot.seek(0)
        image = Image.open(rv_plot)
        width, height = image.size
        logging.info("w: {} h: {}".format(width, height))
        ludo.avatar = rv_plot.getvalue()
    
    ludo.phaselist = results
    ludo.put()
    logging.debug(ludo)
    logging.info("Done with processing")

    return results

    # This scaling code does not seem to work??
    # image.resize((500,200),Image.NEAREST)
    # cimage = io.BytesIO()
    # image.save(cimage,'png')
    # cimage.seek(0)  # rewind to the start
    # ludo.avatar = cimage.getvalue()
