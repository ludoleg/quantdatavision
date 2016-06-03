import logging
import StringIO
# from PIL import Image

import qxrd
import qxrdtools
# import conductor
# import graphit

from logics import QuantMode, QuantModeModel

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

    if(mode == None):
        logging.critical("Current Mode invalid")
        logging.critical("Plugging default")
        mode = QuantModeModel.get_or_insert("DEFAULT")
        mode_key = mode.put()
        session.currentMode = mode_key
        session.put()
        
    logging.debug("Mode ->")
    logging.debug(mode)

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
    
    # Boundaries check
    if(Lambda > 2.2 or Lambda == 0):
        Lambda = ''
    if(FWHMa > 0.01):
        FWHMa = 0.01
    if(FWHMa < -0.01):
        FWHMa = -0.01
    if(FWHMb > 1.0):
        FWHMb = 1.0
    if(FWHMb < 0.01):
        FWHMb = 0.01
        
    # InstrParams = {"Lambda": 0, "Target": '', "FWHMa": -0.001348, "FWHMb": 0.352021}
    InstrParams = {"Lambda": Lambda, "Target": Target, "FWHMa": FWHMa, "FWHMb": FWHMb}

    logging.info("Filename: {}".format(filename))
    logging.info("Target: %s", Target)
    logging.info("Lambda: %s", Lambda)
    logging.info("Fa: %s", FWHMa)
    logging.info("Fb: %s", FWHMb)
    logging.info(mode.title)
    logging.info(mode.inventory)

    logging.debug(InstrParams)
    
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
