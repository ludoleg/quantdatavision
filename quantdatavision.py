import webapp2
from google.appengine.ext.webapp import template

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import users

import StringIO
import numpy as np
#import matplotlib.pyplot as plt

import logging

global user_data

# This datastore model keeps track of which users uploaded which photos.
class UserData(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()

class ShowHome(webapp2.RequestHandler):
    def get(self):
        ## Code to render home page
        temp_data = {}
        temp_path = 'index.html'
        self.response.out.write(template.render(temp_path,temp_data))


class ShowChart(webapp2.RequestHandler):
     def get(self):
#         plt.plot(np.random.random((20)))
#         sio = StringIO.StringIO()
#         plt.savefig(sio, format="png")
#         img_b64 = sio.getvalue().encode("base64").strip()
#         plt.clf()
#         sio.close()
         self.response.write("""<html><body>""")
#         self.response.write("<img src='data:image/png;base64,%s'/>" % img_b64)
         self.response.write("""</body> </html>""")

class DisplayChart(webapp2.RequestHandler):
    def get(self):
        template_data = {}
        template_path = 'chart.html'
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
            logging.debug('User: %s', user_data.user)
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
        self.response.out.write(angle)
        self.response.out.write(diff)

        self.response.out.write("</body></html>")


# [START download_handler]
class ServeDataHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, data_key):
        if not blobstore.get(data_key):
            self.error(404)
        else:
            self.send_blob(data_key)
# [END download_handler]

## Here is the WSGI application instance that routes requests
 
app = webapp2.WSGIApplication([
    ('/view_data',ViewDataHandler),
    ('/serve_data/([^/]+)?', ServeDataHandler),
    ('/upload_data',XRDUploadHandler),
    ('/upload_form',XRDFileUploadFormHandler),
#    ('/chart',ShowChart),
    ('/chart',DisplayChart),
    ('/', ShowHome),
], debug=True)

