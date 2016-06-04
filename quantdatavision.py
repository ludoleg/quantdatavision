import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

import json

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import os
import jinja2

# Applications modules
import chart
from logics import QuantMode, QuantModeModel
from models.session import SessionData

import csv

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def dynamic_png(session_key):
    # rv = StringIO.StringIO()
    twoT, diff, bgpoly, calcdiff = chart.GenerateChart(session_key)
    return twoT, diff, bgpoly, calcdiff
# return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()

# [START image_handler]
class renderImage(webapp2.RequestHandler):
    def get(self):
        obj_key = ndb.Key(urlsafe=self.request.get('img_id'))
        ludo = obj_key.get()
        user_id = users.get_current_user().user_id()
        ludo = SessionData.query(SessionData.user == user_id).get()
        if ludo.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(ludo.avatar)
        else:
            self.response.out.write('No image')
            # [END image_handler]

class ShowHome(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logging.debug('Starting ShowHome')
            ## Code to render home page
            title = "XRD Qanalyze"
            template = JINJA_ENVIRONMENT.get_template('index.html')
            template_vars = {
                'title': title,
            }
            self.response.out.write(template.render(template_vars))
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class chemin(webapp2.RequestHandler):
    def get(self):
        logging.debug('Starting Chemin')
        ## Code to render home page
        title = "XRD Qanalyze - Chemin"
        template = JINJA_ENVIRONMENT.get_template('chemin.html')
        template_vars = {
            'title': title,
        }
        self.response.out.write(template.render(template_vars))
        
class CsvDownloadHandler(webapp2.RequestHandler):
  def get(self):
    # Needs to be refactored server vs client csv generation - currently taking the user session results and dumping
    user = users.get_current_user()
    user_id = users.get_current_user().user_id()
    session = SessionData.query(SessionData.user == user_id).get()

    url_string = self.request.get('key')
    # logging.debug(url_string)
    # logging.debug("Hello CSV")
    # user_key = ndb.Key(urlsafe=url_string)
    # user = user_key.get()
    logging.debug(session.results)
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(session.sampleFilename)
    writer = csv.writer(self.response.out)
    writer.writerow(['Mineral', 'AMCSD', 'Mass %'])
    writer.writerows(session.results)


class crank(webapp2.RequestHandler):
    def get(self):
        user_id = users.get_current_user().user_id()
        logging.debug(user_id)
        session = SessionData.query(SessionData.user == user_id).get()
        logging.debug(session.key)
        angle, diff, bgpoly, calcdiff = dynamic_png(session.key)
#        json_obj = {'angle': angle.tolist(), 'diff': diff.tolist(), 'bgpoly': bgpoly.tolist()}
        json_obj = {
            "filename": session.sampleFilename,
            "angle": angle.tolist(),
            "diff": diff.tolist(),
            "bgpoly": bgpoly.tolist(),
            "calcdiff": calcdiff.tolist(),
            "phases": session.results
            }
        # logging.debug(json.dumps(json_obj))
        self.response.out.write(json.dumps(json_obj))

        
class plotPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('plot.html')
        template_vars = {}
        self.response.out.write(template.render(template_vars))

        
class aboutPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        template_vars = {}
        self.response.out.write(template.render(template_vars))
    

class database(webapp2.RequestHandler):
    def get(self):
        logging.debug("NDB debug")
        user = users.get_current_user()
        if user:
            logging.debug('User found, object instance: %s', user)
            user_id = users.get_current_user().user_id()
            logging.debug('User id: %s', user_id)
            logging.debug(user.user_id())
            logging.debug(user.nickname())

            # Checks for Quant session
            session = SessionData.query(SessionData.user == user_id).get()
            # If not, init a session
            if not session:
                logging.debug("No session")
                session = SessionData(user=user_id,
                                      email=user.nickname()
                )
                session.put()
                session_key = session.put()
                # mode = QuantModeModel(parent=session_key)
                mode = QuantModeModel.get_or_insert("DEFAULT")
                mode_key = mode.put()
                session.currentMode = mode_key
                session.put()

            modes = QuantModeModel.query(ancestor=session.key)

            #key_to_delete = ndb.Key(QuantModeModel, kkk_id)

#            for m in list_of_modes:
                # logging.debug("Mode key id: %s", m.key.id());
                # logging.debug("Mode title: %s", m.title);
                # logging.debug("Mode key: %s", m.key.urlsafe());
 #               logging.debug(m.key.urlsafe)
                
            # query = QuantModeModel.query()
            # getKey = query.get()
            # logging.debug(getKey)
            # logging.debug(getKey.key.urlsafe())

            # mode = QuantModeModel.query(QuantModeModel.qtarget=='Co').get()
            # logging.debug(mode.key.id())

            # ludo = QuantModeModel.get_by_id("Cameron")


            # user_id = users.get_current_user().user_id()
            # session = SessionData.query(SessionData.user == user_id).get()
            # user_data_key = session.key
            # #get ID of entity Key
            # qmode_key = ndb.Key(QuantModeModel, 'cameron', parent=session.key)
            # qmode = qmode_key.get()

            # qmode_key = ndb.Key(QuantModeModel, 'Cameron')
            # key = Key(QuantModeModel, 'Cameron').get()
            # logging.debug(qmode)
                
            self.response.out.write('Done')
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))

    
class processFile(webapp2.RequestHandler):
    def post(self):
        logging.debug("Loading File...")
        user = users.get_current_user()
        if user:
            logging.debug('User found, object instance: %s', user)
            user_id = users.get_current_user().user_id()
            logging.debug('User id: %s', user_id)
            logging.debug(user.user_id())
            logging.debug(user.nickname())

            # Checks for Quant session
            session = SessionData.query(SessionData.user == user_id).get()
            # If not, init a session
            if not session:
                session = SessionData(user=user_id,
                                      email=user.nickname()
                )
                session.put()
                session_key = session.put()
                # mode = QuantModeModel(parent=session_key)
                mode = QuantModeModel.get_or_insert("DEFAULT")
                mode_key = mode.put()
                session.currentMode = mode_key
                session.put()

            session.sampleBlob = self.request.get('file')
            session.sampleFilename = self.request.params["file"].filename
            session_data_key = session.put()
            logging.debug(session.sampleFilename)
            logging.debug(session_data_key)

            # query modes
            modes = QuantModeModel.query(ancestor=session.key)

            for m in modes:
                logging.debug(m.title)

            # Generate image, returns results
            angle, diff, bgpoly, calcdiff = dynamic_png(session.key)

            mode = session.currentMode.get()
            logging.debug(mode.title)
                
            csv = session_data_key.urlsafe()
            template = JINJA_ENVIRONMENT.get_template('chart.html')
            template_vars = {
                'phaselist': session.results,
                'angle': angle.tolist(),
                'diff': diff.tolist(),
                'bgpoly': bgpoly.tolist(),
                'sum': calcdiff.tolist(),
                'url_text': csv,
                'key': session_data_key.urlsafe(),
                'samplename': session.sampleFilename,
                'mode': mode
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.debug("No user -> need login")
            self.redirect(users.create_login_url('/'))
#            self.redirect(users.create_login_url(self.request.url))

class FileUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session for app auth
        user = users.get_current_user()
        if user:
            logging.debug('User found, object instance: %s', user)
            user_id = users.get_current_user().user_id()
            logging.debug('User id: %s', user_id)

            # Checks for Quant session
            session = SessionData.query(SessionData.user == user_id).get()
            # If not, init a session
            if not session:
                session = SessionData(user=user_id,
                                      email=user.nickname(),
                )
                session.put()
                # logging.debug(session.available)
            # logging.debug(session)
            ## Code to render home page
            template = JINJA_ENVIRONMENT.get_template('upload.html')
            template_vars = {
                'upload_form_url': '/process'
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.debug("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))


class handleCalibration(webapp2.RequestHandler):
    logging.debug("handleCalibration")
    def get(self):
        logging.debug("Calibration")
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id() 
            session = SessionData.query(SessionData.user == user_id).get()
            if not session:
                # a = -0.001348 
                # b =  0.352021 
                session = SessionData(user=user_id,
                                      email=user.nickname()
                )
                session_key = session.put()
                mode = QuantModeModel(parent=session_key)
                mode_key = mode.put()
                session.currentMode = mode_key
                session.put()

            # Get the current Mode
            mode = session.currentMode.get()
            # logging.debug(mode)
            template = JINJA_ENVIRONMENT.get_template('calibration.html')
            template_vars = {
                'lambda': mode.qlambda,
                'target': mode.qtarget,
                'a': mode.fwhma,
                'b': mode.fwhmb
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))
    def post(self):
        user_id = users.get_current_user().user_id() 
        session = SessionData.query(SessionData.user == user_id).get()
        mylambda = self.request.get('lambda')
        mytarget = self.request.get('target')
        a = self.request.get('fwhma')
        b = self.request.get('fwhmb')

        logging.debug('Lambda retrieved: %s', mylambda)
        logging.debug('Target retrieved: %s', mytarget)

        mode = session.currentMode.get()
                
        mode.qtarget = self.request.get('target')
        if mylambda:
            mode.qlambda = float(mylambda)
        if a:
            mode.fwhma = float(a)
        if b:
            mode.fwhmb = float(b)
        mode.put()
        # self.redirect('/plot')
        self.redirect('/')

class handlePhase(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id() 
            session = SessionData.query(SessionData.user == user_id).get()
            # Checks for Quant session
            # If not, init a session
            if not session:
                session = SessionData(user=user_id,
                                      email=user.nickname(),
                )

                session_key = session.put()
                mode = QuantModeModel(parent=session_key)
                mode_key = mode.put()
                session.currentMode = mode_key
                session.put()

            # Get the current Mode
            mode = session.currentMode.get()

            logging.debug(mode.selected)
            logging.debug(mode.available)
                            
            template = JINJA_ENVIRONMENT.get_template('phase.html')
            template_vars = {
                'availablephaselist': mode.available,
                'selectedphaselist': mode.selected,
                'mode': mode
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))
    def post(self):
        logging.debug("Post args: %s", self.request.arguments())
        selectedlist = self.request.get_all('selectedphase')
        availlist = self.request.get_all('availablephase')
        logging.debug('Phaselist selected retrieved: %s', selectedlist)
        # logging.debug('Phaselist available retrieved: %s', availlist)
        user_id = users.get_current_user().user_id() 
        session = SessionData.query(SessionData.user == user_id).get()
        mode = session.currentMode.get()
        
        selectedlist.sort()
        availlist.sort()
        
        mode.selected = selectedlist
        mode.available = availlist
        mode.put()
        # self.redirect('/plot')
        self.redirect('/')
        

class Modes(webapp2.RequestHandler):
    def get(self):
        logging.debug("Modes")
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id() 
            session = SessionData.query(SessionData.user == user_id).get()
            logging.debug("session")
            if not session:
                session = SessionData(user=user_id,
                                      email=user.nickname()
                )
                session_key = session.put()
                mode = QuantModeModel(parent=session_key)
                mode_key = mode.put()
                session.currentMode = mode_key
                session.put()

            # list_of_modes = ndb.get_multi(session.modes)
            # logging.debug(list_of_modes)
            # for k in list_of_modes:
            #     logging.debug(k.title)
            # logging.debug(len(list_of_modes))
            # for m in list_of_modes:
            #     logging.debug(m)

            mode = QuantMode()
            list = mode.list_mode()
            
            template_vars = {'modes' : mode.list_mode()}
            template = JINJA_ENVIRONMENT.get_template('modes.html')
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))
    def post(self):
        user = users.get_current_user()
        if user:
            if self.request.POST.get('delete'): #if user clicks "Delete" button
                #Sending back the key id from the modes to be deleted
                modes_ids = self.request.get_all('mode_id')
                logging.debug(modes_ids)
                mode = QuantMode()
                mode.delete_mode(modes_ids)
                self.redirect('/modes')

            
        
class activeMode(webapp2.RequestHandler):
    def get (self):
        logging.debug("Active Mode")
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id() 
            session = SessionData.query(SessionData.user == user_id).get()
            logging.debug("session")
            if not session:
                 session = SessionData(user=user_id,
                                      email=user.nickname(),
                 )
                 session.put()
            # logging.debug(session)

            # list_of_modes = ndb.get_multi(session.modes)
            # logging.debug(list_of_modes)
            # for k in list_of_modes:
            #     logging.debug(k.title)
            # logging.debug(len(list_of_modes))
            # for m in list_of_modes:
            #     logging.debug(m)

            currentMode = session.currentMode.get()
            logging.debug(currentMode)
            activeTitle = currentMode.title
            
            mode = QuantMode()
            list = mode.list_mode()
            
            template_vars = {
                'modes' : mode.list_mode(),
                'title': activeTitle
            }
            template = JINJA_ENVIRONMENT.get_template('activeMode.html')
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.url))
    def post(self):
        #get all input values
        user_id = users.get_current_user().user_id() 
        session = SessionData.query(SessionData.user == user_id).get()
        active_mode = self.request.get('mode').strip()
        logging.debug(active_mode)

        qmode_k = ndb.Key('QuantModeModel', int(active_mode), parent=session.key)
        logging.debug(qmode_k)
        session.currentMode = qmode_k
        session.put()
        self.redirect('/')

        
class ModesEditHandler(webapp2.RequestHandler):
    def get (self):
        logging.debug("Edit Modes")
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id()
            session = SessionData.query(SessionData.user == user_id).get()
            user_data_key = session.key
            # Key of QuantModeModel entity
            logging.debug(self.request.get('id'))
            key_id = self.request.get('id')
            
	    mode= ndb.Key('QuantModeModel', int(key_id), parent=session.key).get()
            # mode = ndb.Key(urlsafe=key_str).get()
            logging.debug(mode)
            template_values = { 'mode' : mode,
                                'key': key_id
            }
            template = JINJA_ENVIRONMENT.get_template('modesEdit.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
        #get all input values
        mode_key_id = self.request.get('key_id')
        logging.debug(mode_key_id)
        input_qtarget = self.request.get('target').strip()
        input_qlambda = self.request.get('lambda').strip()
        logging.debug(input_qlambda)
        input_fwhma = self.request.get('fwhma').strip()
        logging.debug(input_fwhma)
        input_fwhmb = self.request.get('fwhmb').strip()
        logging.debug(input_fwhmb)
        input_inventory = self.request.get('inventory').strip()
        logging.debug(input_inventory)
        input_description = self.request.get('desc').strip()
        logging.debug(input_description)

        mode = QuantMode()
        mode.save_mode(0, input_description, input_qtarget, float(input_qlambda), float(input_fwhma), float(input_fwhmb), input_inventory, int(mode_key_id))
        self.redirect('/modes')


class ModesCreateHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template('modesCreate.html')
            self.response.out.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
        logging.debug("Create Modes")
        #get all input values
        qtarget = self.request.get('target').strip()
        qlambda = self.request.get('lambda').strip()
        fwhma = self.request.get('fwhma').strip()
        fwhmb = self.request.get('fwhmb').strip()
        title = self.request.get('modeTitle').strip()
        inventory = self.request.get('inventory').strip()
        description = self.request.get('modeDesc').strip()

        # Populate the phaselist according to the inventory choice
        # Read in the file
        jump = 1
        if inventory == "cement":
            phaselistname = 'difdata_cement_inventory.csv'
        elif inventory == "pigment":
            phaselistname = 'difdata_pigment_inventory.csv'
        elif inventory == "rockforming":
            phaselistname = 'difdata-rockforming_inventory.csv'
        elif inventory == "chemin":
            phaselistname = 'difdata_CheMin_inventory.csv'
        else:
            logging.debug("Can't find inventory")

        phaselist = open(phaselistname, 'r').readlines()[jump:]

        phaselist.sort()
        logging.debug(phaselist)

        user_id = users.get_current_user().user_id()
        session = SessionData.query(SessionData.user == user_id).get()

        # Mode creation: last parameter = 0
        # mode = QuantMode()
        # mode.save_mode(title ,qtarget, float(qlambda), float(fwhma), float(fwhmb), inventory, phaselist, 0)

        # Create mode
	qmode = QuantModeModel(title=title, parent=session.key)

	qmode.qlambda = float(qlambda)
	qmode.qtarget = qtarget
	qmode.fwhma = float(fwhma)
	qmode.fwhmb = float(fwhmb)
        qmode.inventory = inventory
        qmode.description = description
        qmode.selected = phaselist
        qmode.available = []

	key = qmode.put()
        
        session.currentMode = key
        session.put()
        
        # mode = QuantModeModel(title=title,
        #                       qlambda=float(qlambda),
        #                       qtarget=qtarget,
        #                       fwhma=float(fwhma),
        #                       fwhmb=float(fwhmb))
        # key = mode.put()

        # user_id = users.get_current_user().user_id() 
        # session = SessionData.query(SessionData.user == user_id).get()

        # session.modes.append(key)
        # session.put()
        
        # list_of_modes = ndb.get_multi(session.modes)
        # for k in list_of_modes:
        #     logging.debug(k)
        
        # logging.debug(session)

        self.redirect('/modes')


class leave(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

        
class isLogged(webapp2.RequestHandler):
    def get(self):
        username = ''
        user = users.get_current_user()
        if user:
            # username = 'Login'
            username = user.nickname()
        else:
            username = 'Not logged in'
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(username))
        
# logging.getLogger().setLevel(logging.DEBUG)

## Here is the WSGI application instance that routes requests
app = webapp2.WSGIApplication([
    ('/about', aboutPage),
    ('/activeMode', activeMode),
    ('/phase', handlePhase),
    ('/calibration', handleCalibration),
    ('/chemin', chemin),
    ('/csv',CsvDownloadHandler),
    ('/crank', crank),
    ('/img', renderImage),
    ('/isLogged', isLogged ),
    ('/leave', leave ),
    ('/modes', Modes),
    ('/modes/create', ModesCreateHandler),
    ('/modes/edit', ModesEditHandler),
    ('/ndb', database ),
    ('/plot', plotPage),
    ('/process', processFile),
    ('/upload_form', FileUploadFormHandler ),
    ('/', ShowHome),
], debug=True)

