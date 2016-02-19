import globals
import webapp2
#from google.appengine.ext.webapp import template

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb

from google.appengine.api import users

import StringIO
import logging
import chart
from chart import UserData

import os
import jinja2

from io import BytesIO

# [START import_images]
from google.appengine.api import images
from PIL import Image

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+ "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

import csv
# import json

def dynamic_png(key):
    rv = StringIO.StringIO()
    rv = chart.GenerateChart(key)
    logging.debug(rv)
    return rv
#        return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()

# [START image_handler]
class Image(webapp2.RequestHandler):
    def get(self):
        ludo_key = ndb.Key(urlsafe=self.request.get('img_id'))
        ludo = ludo_key.get()
        if ludo.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(ludo.avatar)
        else:
            self.response.out.write('No image')
# [END image_handler]
        
class ShowHome(webapp2.RequestHandler):
    def get(self):
        logging.debug('Starting ShowHome')

        user = users.get_current_user()
        logging.debug('User object instance: %s', user)

        # Checks for active Google account session
        if user:
            user_id = users.get_current_user().user_id()
            logging.debug('User id: %s', user_id)
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
            self.redirect(users.create_login_url(self.request.uri))

        
class DisplayChart(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('displayChart.html')
        self.response.out.write(template.render())
         
class XRDFileUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        # [START upload_url]
        upload_url = blobstore.create_upload_url('/upload_data')
        # [START upload_form]
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        template_vars = {
            'upload_form_url': upload_url
        }
        self.response.out.write(template.render(template_vars))
        # To upload files to the blobstore, the request method must be "POST"
        # and enctype must be set to "multipart/form-data".
        # [END upload_form]
        
class XRDUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            logging.debug('Starting Upload')
            upload = self.get_uploads()[0]
            user_data = UserData(
                user=users.get_current_user().user_id(),
                blob_key=upload.key())

            if globals.OSX:
                imgfile = open('cristal.jpg','r')
                user_data.avatar = imgfile.read()

            user_data_key = user_data.put()

            # NDB instance Key
            logging.debug(user_data_key)

            # NDB get instance from Key
            ludo = user_data_key.get()
            logging.debug("ludo: %s", ludo)

            kind_string = user_data_key.kind()
            logging.debug(kind_string)

            id = user_data_key.id()
            logging.debug(id)

            url_string = user_data_key.urlsafe()
            logging.debug(url_string)

            ludo_key = ndb.Key(urlsafe=url_string)
            logging.debug(ludo_key)
            
            key = ndb.Key(urlsafe=url_string)
            logging.debug(key)

            kind_string = key.kind()
            logging.debug(kind_string)
            id = key.id()
                        
            logging.debug(user_data)
            # user_data_key = ndb.Key('UserData', user_data)

            logging.debug('User_data: %s', user_data.user)
            logging.debug('Blobkey: %s', user_data.blob_key)

            #self.redirect('/serve_data/%s' % upload.key())
            self.redirect('/serve_data/%s' % url_string)

        except:
            self.error(500)

# [START data_view_handler]
class ViewDataHandler(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        logging.debug('User: %s', user)
        obj = UserData.query(UserData.user == user).get()
        template = JINJA_ENVIRONMENT.get_template('data.html')
        template_vars = {
            'phaselist': obj.phaselist
        }
        self.response.out.write(template.render(template_vars))

class imageHandler(webapp2.RequestHandler):
    def post(self):
        user_id = users.get_current_user().user_id() 
        ludo = UserData.query(UserData.user == user_id).get()
        avatar = self.request.get('img')
        logging.debug("starting imageHandler")
        logging.debug(avatar)
        avatar = images.resize(avatar, 128, 128)
        ludo.avatar = avatar
        ludo.put()
        self.redirect('/')

class showProfile(webapp2.RequestHandler):
    def get(self):
        logging.debug("starting profile")
        user = users.get_current_user()
        logging.debug('User: %s', user)
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        template_vars = {
            'user': user,
            'imageHandler': "/processImage"
        }
        self.response.out.write(template.render(template_vars))

# [START download_handler]
class ServeDataHandler(blobstore_handlers.BlobstoreDownloadHandler):
     def get(self, data_key):
        my_key = ndb.Key(urlsafe=data_key) 
        logging.debug('Safeurl key: %s', my_key)
        ludo = my_key.get()
        
        if not blobstore.get(ludo.blob_key):
            self.error(404)
        else:
            user = users.get_current_user()
            logout = users.create_logout_url('/')
            res = dynamic_png(my_key)
            blob_info = blobstore.BlobInfo.get(ludo.blob_key)
            filename = blob_info.filename
            # self.response.write(ludo.phaselist)
            # results_json = json.dumps(res, indent=4, separators=(',\n', ': '))
            csv = my_key.urlsafe()
            template = JINJA_ENVIRONMENT.get_template('chart.html')
            template_vars = {
                'phaselist': ludo.phaselist,
                'url_text': csv,
                'logout_url': logout,
                'user': user.nickname(),
                'key': my_key.urlsafe(),
                'samplename': filename
            }
            self.response.out.write(template.render(template_vars))

# [END download_handler]

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

    
## Here is the WSGI application instance that routes requests
logging.getLogger().setLevel(logging.INFO)

app = webapp2.WSGIApplication([
    ('/view_data',ViewDataHandler),
    ('/serve_data/([^/]+)?', ServeDataHandler),
    ('/upload_data',XRDUploadHandler),
    ('/upload_form',XRDFileUploadFormHandler),
    ('/csv',CsvDownloadHandler),
    ('/chart',DisplayChart),
    ('/profile',showProfile),
    ('/processImage',imageHandler),
    ('/img', Image),
    ('/', ShowHome),
], debug=True)



        # ludo = UserData.query(UserData.user == user_id).get()
        # logging.debug(ludo)
        # ludo_key = ludo.key
        # logging.debug(ludo_key)
        
        # ludo_url = ludo_key.urlsafe()
        # logging.debug(ludo_url)
        
# <h1>{{ key }}</h1>
# <div><img src="/img?img_id={{ key }}"></img>
