import logging
import QXRDconductor
from google.appengine.ext import ndb

import StringIO
from PIL import Image

Lambda = ''
Target = ''

# This datastore model keeps track of which users uploaded which photos.
class UserData(ndb.Model):
    user = ndb.StringProperty()
    phaselist = ndb.PickleProperty()
    avatar = ndb.BlobProperty()
    sampleFilename = ndb.StringProperty()
    sampleBlob = ndb.BlobProperty()
    

def GenerateChart(obj_key):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    logging.info("Start with processing...")
    ludo = obj_key.get()
    # logging.debug(ludo)

    # Logic with simple file upload
    filename = ludo.sampleFilename
    
    logging.debug("Filename: {}".format(filename))
    # Logic to parse correct file
    
    # Logic with simple file upload
    XRDdata = StringIO.StringIO(ludo.sampleBlob)
    logging.debug(XRDdata)
    
    phaselistname = 'phaselist.csv'
    phaselist = open(phaselistname, 'r').readlines()
    DBname = "reduced_difdata.txt"
    difdata = open(DBname, 'r').readlines()

    # logging.debug(XRDdata)
    logging.info("Start Quant.phase...")
    
    #if globals.OSX:
    #    results = QUANT.PhaseAnalyze(XRDdata,difdata,phaselist)
    #    file = open("cristal.jpg")
    #    ludo.avatar = file.read()
    # else:
    rv_plot = StringIO.StringIO()
    twoT, diff = QXRDconductor.openXRD(XRDdata, filename)
    results, rv_plot = QXRDconductor.Qanalyze(twoT, diff, difdata, phaselist, Lambda, Target)
    rv_plot.seek(0)
    image = Image.open(rv_plot)
    width, height = image.size
    # logging.info("w: {} h: {}".format(width, height))
    ludo.avatar = rv_plot.getvalue()
    
    ludo.phaselist = results
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
