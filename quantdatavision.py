import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users

import cgi

import logging
import chart
from chart import SessionData
import StringIO

import os
import jinja2

import phaselist

from google.appengine.api import images
from PIL import Image

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
        ludo_key = ndb.Key(urlsafe=self.request.get('img_id'))
        ludo = ludo_key.get()
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

        # Checks for active Google account session
        user = users.get_current_user()
        if user:
            logging.debug('User found, object instance: %s', user)
            user_id = users.get_current_user().user_id()
            logging.debug('User id: %s', user_id)

            # Checks for Quant session
            ludo = SessionData.query(SessionData.user == user_id).get()
            # If not, create a session
            if not ludo:
                ludo = SessionData(user=user_id, email=user.nickname())
                # Needed populate the phase list - Initialize with all phases
                ludo.available = phaselist.availablePhases
                ludo.put()
                logging.debug(ludo.available)
                
            logging.debug(ludo)
                
            ## Code to render home page
            title = "Welcome to PLQuant"
            template = JINJA_ENVIRONMENT.get_template('index.html')
            template_vars = {
                'title': title,
                'user': user
            }
            self.response.out.write(template.render(template_vars))
            #self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            #self.response.write('Hello, ' + user.nickname())
        else:
            logging.debug("No user -> need login")
            self.redirect(users.create_login_url(self.request.uri))

# [START data_view_handler]
class ViewDataHandler(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        logging.debug('User: %s', user)
        obj = SessionData.query(SessionData.user == user).get()
        template = JINJA_ENVIRONMENT.get_template('data.html')
        template_vars = {
            'phaselist': obj.phaselist
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

class setPhase(webapp2.RequestHandler):
    def get(self):
        user_id = users.get_current_user().user_id() 
        ludo = SessionData.query(SessionData.user == user_id).get()
        template = JINJA_ENVIRONMENT.get_template('phase.html')
        template_vars = {
            'availablephaselist': ludo.available,
            'selectedphaselist': ludo.selected
        }
        self.response.out.write(template.render(template_vars))

class handlePhase(webapp2.RequestHandler):
    def post(self):
        logging.debug("Post args: %s", self.request.arguments())
        selectedlist = self.request.get_all('selectedphase')
        availlist = self.request.get_all('availablephase')
        logging.debug('Phaselist selected retrieved: %s', selectedlist)
        logging.debug('Phaselist available retrieved: %s', availlist)
        user_id = users.get_current_user().user_id() 
        ludo = SessionData.query(SessionData.user == user_id).get()
        ludo.selected = selectedlist
        ludo.available = availlist
        ludo.put()
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
        logging.debug("Do I get here?")
        self.response.out.write(template.render(template_vars))

# [START download_handler]
class FileUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        template_vars = {
            'upload_form_url': '/process'
        }
        self.response.out.write(template.render(template_vars))
    
## Here is the WSGI application instance that routes requests
logging.getLogger().setLevel(logging.DEBUG)

app = webapp2.WSGIApplication([
    ('/csv',CsvDownloadHandler),
    ('/img', renderImage),
    ('/phase', setPhase),
    ('/calibration', setPhase),
    ('/process', processFile),
    ('/savePhase', handlePhase),
    ('/upload_form', FileUploadFormHandler ),
    ('/', ShowHome),
], debug=True)

