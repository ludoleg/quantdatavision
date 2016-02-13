import webapp2
from google.appengine.ext.webapp import template

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import users

import StringIO
import logging
import chart

import numpy as np

def dynamic_png(key):
    blob_reader = blobstore.BlobReader(key)
    rv = StringIO.StringIO()
    rv = chart.GenerateChart(blob_reader)
    # logging.debug(results)
    return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()

# This datastore model keeps track of which users uploaded which photos.
class UserData(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()

class ShowHome(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        logging.debug('Starting ShowHome')
        user = users.get_current_user()
        if user:
            ## Code to render home page
            temp_data = {}
            temp_path = 'index.html'
            self.response.out.write(template.render(temp_path,temp_data))
            #self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            #self.response.write('Hello, ' + user.nickname())
        else:
            self.redirect(users.create_login_url(self.request.uri))

        
class DisplayChart(webapp2.RequestHandler):
    def get(self):
        template_data = {}
        template_path = 'displayChart.html'
        self.response.out.write(template.render(template_path,template_data))
         
class XRDFileUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        # [START upload_url]
        upload_url = blobstore.create_upload_url('/upload_data')
        # [END upload_url]
        # [START upload_form]
        # To upload files to the blobstore, the request method must be "POST"
        # and enctype must be set to "multipart/form-data".
        self.response.out.write("""
<html><body>
<form action="{0}" method="POST" enctype="multipart/form-data">
  Upload File: <input type="file" name="file"><br>
  <input type="submit" name="submit" value="Submit">
</form>
</body></html>""".format(upload_url))
        # [END upload_form]
        
class XRDUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            user_data = UserData(
                user=users.get_current_user().user_id(),
                blob_key=upload.key())
            logging.info('User: %s', user_data.user)
            logging.debug('Blobkey: %s', user_data.blob_key)
            user_data.put()

            self.redirect('/serve_data/%s' % upload.key())

        except:
            self.error(500)

# [START data_view_handler]
class ViewDataHandler(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user().user_id()
        logging.debug('User: %s', user)
        qry = UserData.query(UserData.user == user).get()
        my_key = qry.blob_key
        logging.debug('Key: %s', my_key)

        self.response.out.write("<html><body>")
        self.response.out.write("<p>Welcome to Data Quant!</p>")

        # Instantiate a BlobReader for a given Blobstore value.
        blob_reader = blobstore.BlobReader(my_key)
        angle, diff = np.loadtxt(blob_reader, unpack=True)
        
        # for line in blob_reader:
        #     self.response.out.write(line.replace("\r\n", "<br/>"))
        #     self.response.out.write(line)
        self.response.out.write("Angle<br/>")
        self.response.out.write(angle)
        self.response.out.write("Diff<br/>")
        self.response.out.write(diff)

        self.response.out.write("</body></html>")


# [START download_handler]
class ServeDataHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, data_key):
        logging.debug('Download handler Key: %s', data_key)
        if not blobstore.get(data_key):
            self.error(404)
        else:
            user = users.get_current_user()
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %(user.nickname(), users.create_logout_url('/')))
            self.response.write("""<html><head><title>Cristallography</title></head><body>""")
            self.response.write(dynamic_png(data_key))
            self.response.write("%s" % greeting)
            self.response.write("""</body> </html>""")
# [END download_handler]

## Here is the WSGI application instance that routes requests
logging.getLogger().setLevel(logging.DEBUG)

app = webapp2.WSGIApplication([
    ('/view_data',ViewDataHandler),
    ('/serve_data/([^/]+)?', ServeDataHandler),
    ('/upload_data',XRDUploadHandler),
    ('/upload_form',XRDFileUploadFormHandler),
    ('/chart',DisplayChart),
    ('/', ShowHome),
], debug=True)

