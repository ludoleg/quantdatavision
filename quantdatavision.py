import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

import logging
import StringIO

import os
import jinja2

# Applications modules
import chart
from chart import SessionData

import phaselist
import csv

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+ "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def dynamic_png(key):
    rv = StringIO.StringIO()
    rv = chart.GenerateChart(key)
    # logging.debug(rv)
    return rv
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
        logging.debug('Starting ShowHome')
        ## Code to render home page
        title = "XRD Qanalyze"
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_vars = {
            'title': title,
        }
        self.response.out.write(template.render(template_vars))

class CsvDownloadHandler(webapp2.RequestHandler):
  def get(self):
    url_string = self.request.get('key')
    logging.debug(url_string)
    logging.debug("Hello CSV")
    user_key = ndb.Key(urlsafe=url_string)
    user = user_key.get()
    logging.debug(user.phaselist)
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.headers['Content-Disposition'] = 'attachment; filename=phaselist.csv'
    writer = csv.writer(self.response.out)
    writer.writerow(['Mineral','Mass %'])
    writer.writerows(user.phaselist)


class aboutPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        template_vars = {}
        self.response.out.write(template.render(template_vars))
    
class setPhase(webapp2.RequestHandler):
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
                                      qtarget = "Co",
                                      qlambda=0,
                                      available = phaselist.availablePhases,
                                      selected = phaselist.defaultPhases)
                session.put()
            template = JINJA_ENVIRONMENT.get_template('phase.html')
            template_vars = {
                'availablephaselist': session.available,
                'selectedphaselist': session.selected
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.uri))

class setCalibration(webapp2.RequestHandler):
    def get(self):
        logging.debug("Calibration")
        user = users.get_current_user()
        if user:
            user_id = users.get_current_user().user_id() 
            session = SessionData.query(SessionData.user == user_id).get()

            if not session:
                session = SessionData(user=user_id,
                                      email=user.nickname(),
                                      qtarget = "Co",
                                      qlambda=0,
                                      available = phaselist.availablePhases,
                                      selected = phaselist.defaultPhases)
                session.put()
            # logging.debug(session)
            template = JINJA_ENVIRONMENT.get_template('calibration.html')
            template_vars = {
                'lambda': session.qlambda,
                'target': session.qtarget,
            }
            self.response.out.write(template.render(template_vars))
        else:
            logging.info("No user -> need login")
            self.redirect(users.create_login_url(self.request.uri))
        
class handleCalibration(webapp2.RequestHandler):
    def post(self):
        logging.debug("handleCalibration")
        user_id = users.get_current_user().user_id() 
        session = SessionData.query(SessionData.user == user_id).get()
        mylambda = self.request.get('lambda')
        mytarget = self.request.get('target')
        ludo = float(mylambda)
        logging.debug('Lambda retrieved: %s', mylambda)
        logging.debug('Lambda retrieved: %f', ludo)
        logging.debug('Target retrieved: %s', mytarget)
        session.qlambda = ludo
        session.qtarget = self.request.get('target')
        session.put()
        self.redirect('/')

class handlePhase(webapp2.RequestHandler):
    def post(self):
        logging.debug("Post args: %s", self.request.arguments())
        selectedlist = self.request.get_all('selectedphase')
        availlist = self.request.get_all('availablephase')
        logging.debug('Phaselist selected retrieved: %s', selectedlist)
        # logging.debug('Phaselist available retrieved: %s', availlist)
        user_id = users.get_current_user().user_id() 
        session = SessionData.query(SessionData.user == user_id).get()
        selectedlist.sort()
        availlist.sort()
        session.selected = selectedlist
        session.available = availlist
        session.put()
        self.redirect('/')
    
class processFile(webapp2.RequestHandler):
    def post(self):
        logging.debug("Loading File...")
        user = users.get_current_user()
        if user:
            logging.debug('User signed, object instance: %s', user)
        logging.debug(user.user_id())
        logging.debug(user.nickname())
        logout = users.create_logout_url('/')
        user_id = users.get_current_user().user_id()
        logging.debug(user_id)
        ludo = SessionData.query(SessionData.user == user_id).get()
        if not ludo:
            ludo = SessionData(user=user_id, email=user.nickname())
        ludo.sampleBlob = self.request.get('file')
        ludo.sampleFilename = self.request.params["file"].filename
        user_data_key = ludo.put()
        logging.debug(ludo.sampleFilename)
        logging.debug(user_data_key)

        # Generate image, returns results
        results = dynamic_png(user_data_key)
        csv = user_data_key.urlsafe()
        template = JINJA_ENVIRONMENT.get_template('chart.html')
        template_vars = {
            'phaselist': ludo.results,
            'url_text': csv,
            'logout_url': logout,
            'user': user.nickname(),
            'key': user_data_key.urlsafe(),
            'samplename': ludo.sampleFilename
        }
        self.response.out.write(template.render(template_vars))

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
                                      qtarget = "Co",
                                      qlambda=0,
                                      available = phaselist.availablePhases,
                                      selected = phaselist.defaultPhases)
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
            self.redirect(users.create_login_url(self.request.uri))
        
class leave(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))
        
logging.getLogger().setLevel(logging.DEBUG)
        
## Here is the WSGI application instance that routes requests
app = webapp2.WSGIApplication([
    ('/phase', setPhase),
    ('/calibration', setCalibration),
    ('/savePhase', handlePhase),
    ('/saveCal', handleCalibration),
    ('/about', aboutPage),
    ('/csv',CsvDownloadHandler),
    ('/img', renderImage),
    ('/process', processFile),
    ('/upload_form', FileUploadFormHandler ),
    ('/leave', leave ),
    ('/', ShowHome),
], debug=True)

