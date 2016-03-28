import logging
import conductor
from google.appengine.ext import ndb

import StringIO
from PIL import Image

# This datastore model keeps track of which users uploaded which photos.
class SessionData(ndb.Model):
    user = ndb.StringProperty()
    email = ndb.StringProperty()
    selected = ndb.PickleProperty()
    available = ndb.PickleProperty()
    results = ndb.PickleProperty()
    avatar = ndb.BlobProperty()
    sampleFilename = ndb.StringProperty()
    sampleBlob = ndb.BlobProperty()
    qlambda = ndb.FloatProperty()
    qtarget = ndb.StringProperty()
    fwhma = ndb.FloatProperty()
    fwhmb = ndb.FloatProperty()
    
def GenerateChart(obj_key):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    logging.info("Start with processing...")
    ludo = obj_key.get()
    # logging.debug(ludo)

    # Logic with simple file upload
    filename = ludo.sampleFilename

    # Calibration parameters
    Lambda = ludo.qlambda
    Target = ludo.qtarget
    FWHMa = ludo.fwhma
    FWHMb = ludo.fwhmb
    
    if(Lambda > 2.2 or Lambda == 0):
        Lambda = ''
    
    logging.debug("Filename: {}".format(filename))
    logging.debug("Target: %s", Target)
    logging.debug("Lambda: %s", Lambda)
    # Logic to parse correct file
    
    # Logic with simple file upload
    XRDdata = StringIO.StringIO(ludo.sampleBlob)
    logging.debug(XRDdata)
    
    phaselistname = 'phaselist.csv'
    phaselist = open(phaselistname, 'r').readlines()
    selectedPhases = ludo.selected
    
    DBname = "reduced_difdata.txt"
    difdata = open(DBname, 'r').readlines()

    # logging.debug(XRDdata)
    logging.info("Start Quant.phase...")
    
    rv_plot = StringIO.StringIO()
    twoT, diff = conductor.openXRD(XRDdata, filename)
    results, rv_plot = conductor.Qanalyze(twoT, diff, difdata, phaselist, selectedPhases, Lambda, Target, FWHMa, FWHMb)
    rv_plot.seek(0)
    image = Image.open(rv_plot)
    width, height = image.size
    # logging.info("w: {} h: {}".format(width, height))
    ludo.avatar = rv_plot.getvalue()
    
    # ludo.selected = results
    ludo.results = results
    ludo.put()
    # logging.debug(ludo)

    logging.debug(results)
    logging.info("Done with processing")

    return diff

    # This scaling code does not seem to work??
    # image.resize((500,200),Image.NEAREST)
    # cimage = io.BytesIO()
    # image.save(cimage,'png')
    # cimage.seek(0)  # rewind to the start
    # ludo.avatar = cimage.getvalue()
