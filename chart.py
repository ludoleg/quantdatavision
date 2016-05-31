import logging

import StringIO
from PIL import Image

import qxrd
import qxrdtools
# import conductor
import graphit

def GenerateChart(obj_key):
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    logging.info("Start with processing...")
    session = obj_key.get()
    logging.debug(session)

    # Logic with simple file upload
    filename = session.sampleFilename

    mode_key = session.currentMode
    logging.debug(mode_key)
    mode = mode_key.get()

    # Unpack the selected inventory
    logging.debug(mode.title)
    logging.debug(mode.qlambda)
    logging.debug(mode.inventory)

    if mode.inventory == "cement":
        # phaselistname = 'difdata_cement_inventory.csv'
        DBname ='difdata_cement.txt'
    elif mode.inventory == "pigment":
        # phaselistname = 'difdata_pigment_inventory.csv'
        DBname ='difdata_pigment.txt'
    elif mode.inventory == "rockforming":
        # phaselistname = 'difdata-rockforming_inventory.csv'
        DBname ='difdata-rockforming.txt'
    elif mode.inventory == "chemin":
        # phaselistname = 'difdata_CheMin_inventory.csv'
        DBname ='difdata_CheMin.txt'
    else:
        logging.debug("Can't find inventory")

    # Calibration parameters
    # Lambda = session.qlambda
    # Target = session.qtarget
    # FWHMa = session.fwhma
    # FWHMb = session.fwhmb
    Lambda = mode.qlambda
    Target = mode.qtarget
    FWHMa = mode.fwhma
    FWHMb = mode.fwhmb
    
    if(Lambda > 2.2 or Lambda == 0):
        Lambda = ''
    
    logging.debug("Filename: {}".format(filename))
    logging.debug("Target: %s", Target)
    logging.debug("Lambda: %s", Lambda)
    logging.debug("Fa: %d", FWHMa)
    logging.debug("Fb: %d", FWHMb)
    # Logic to parse correct file
    
    # Logic with simple file upload
    XRDdata = StringIO.StringIO(session.sampleBlob)
    logging.debug(XRDdata)
    
    # phaselistname = 'phaselist.csv'
    # phaselist = open(phaselistname, 'r').readlines()
    mode = session.currentMode.get()
    selectedPhases = mode.selected
    
    # DBname = "reduced_difdata.txt"
    difdata = open(DBname, 'r').readlines()

    # logging.debug(XRDdata)
    logging.info("Start Quant.phase...")
    
    rv_plot = StringIO.StringIO()
    # twoT, diff = qxrdtools.openXRD(XRDdata, filename)

    # 
    userData = qxrdtools.openXRD(XRDdata, filename)
    # logging.debug(userData)

    InstrParams = {"Lambda": 0, "Target": '', "FWHMa": -0.001348, "FWHMb": 0.352021}

    # Dif data captures all cristallographic data
    selectedphases = []
    for i in range (1, len(selectedPhases)):
        name, code = selectedPhases[i].split('\t')
        code = int(code)
        selectedphases.append((name,code))

    results, BG, calcdiff = qxrd.Qanalyze(userData, difdata, selectedphases, InstrParams)

    # results, BG, calcdiff =      conductor.Qanalyze(twoT, diff ,difdata, phaselist, selectedPhases, Lambda, Target, FWHMa, FWHMb)

    # rv_plot = graphit.overplotgraph(twoT,diff,BG,calcdiff, results[0:min(10,len(results))], filename)
    
    # rv_plot.seek(0)
    # image = Image.open(rv_plot)
    # width, height = image.size
    # logging.info("w: {} h: {}".format(width, height))
    # session.avatar = rv_plot.getvalue()
    
    session.results = results
    session.put()

    logging.debug(results)
    logging.info("Done with processing")

    twoT = userData[0]
    diff = userData[1]
    
    return twoT, diff, BG, calcdiff

    # This scaling code does not seem to work??
    # image.resize((500,200),Image.NEAREST)
    # cimage = io.BytesIO()
    # image.save(cimage,'png')
    # cimage.seek(0)  # rewind to the start
    # session.avatar = cimage.getvalue()
