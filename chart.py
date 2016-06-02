import logging
import StringIO
# from PIL import Image

import qxrd
import qxrdtools
# import conductor
# import graphit

def GenerateChart(obj_key):
    """ Execute diffraction computation and returns arrays of (x,y) datat for graph rendering """
    
    ##############################################################################
    ############   Program parameters   ##########################################
    ##############################################################################
    logging.info("Start with processing...")

    # Get the current session & mode
    session = obj_key.get()
    # mode_key = session.currentMode
    # mode = mode_key.get()
    mode = session.currentMode.get()
    logging.info("Mode ->")
    logging.info(mode)

    # Load the sample data file in userData
    # parse sample data file wrt format
    filename = session.sampleFilename
    XRDdata = StringIO.StringIO(session.sampleBlob)
    # logging.debug(XRDdata)
    userData = qxrdtools.openXRD(XRDdata, filename)
    # logging.debug(userData)

    # Unpack the selected inventory
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
        logging.critical("Can't find inventory")

    # Calibration parameters
    Lambda = mode.qlambda
    Target = mode.qtarget
    FWHMa = mode.fwhma
    FWHMb = mode.fwhmb
    
    if(Lambda > 2.2 or Lambda == 0):
        Lambda = ''
    
    # InstrParams = {"Lambda": 0, "Target": '', "FWHMa": -0.001348, "FWHMb": 0.352021}
    InstrParams = {"Lambda": Lambda, "Target": Target, "FWHMa": FWHMa, "FWHMb": FWHMb}

    logging.debug("Filename: {}".format(filename))
    logging.debug("Target: %s", Target)
    logging.debug("Lambda: %s", Lambda)
    logging.debug("Fa: %d", FWHMa)
    logging.debug("Fb: %d", FWHMb)
    logging.debug(mode.title)
    logging.debug(mode.inventory)
    
    # Phase selection
    selectedPhases = mode.selected
    # Dif data captures all cristallographic data
    selectedphases = []
    for i in range (len(selectedPhases)):
        name, code = selectedPhases[i].split('\t')
        code = int(code)
        selectedphases.append((name,code))
    logging.debug(selectedphases)
    
    # Load in the DB file
    difdata = open(DBname, 'r').readlines()
    
    # rv_plot = StringIO.StringIO()
    # twoT, diff = qxrdtools.openXRD(XRDdata, filename)
        
    # UserData = sample file = XRDdata stripped of header/format specific info    
    # Difdata = mineral database with all the info compiled by univ - text format
    # selectedphases = phaselist in name/AMCSD format
    # InstrParams = instrumentation parameters
    logging.info("Start qxrd.Qanalyze...")
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

    twoT = userData[0]
    diff = userData[1]

    logging.debug(results)
    logging.info("Done with processing")
    
    return twoT, diff, BG, calcdiff

    # This scaling code does not seem to work??
    # image.resize((500,200),Image.NEAREST)
    # cimage = io.BytesIO()
    # image.save(cimage,'png')
    # cimage.seek(0)  # rewind to the start
    # session.avatar = cimage.getvalue()
