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

from google.appengine.api import images
from PIL import Image

import numpy as np
from scipy import special, optimize
import matplotlib.pyplot as plt

import csv

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+ "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def dynamic_png(key):
    rv = StringIO.StringIO()
    rv = chart.GenerateChart(key)
    logging.debug(rv)
    return rv
#        return """<img src="data:image/png;base64,%s"/>""" % rv.getvalue().encode("base64").strip()

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

class testscipy(webapp2.RequestHandler):
    def get(self):
        # Parse command-line arguments
        # parser = argparse.ArgumentParser(usage=__doc__)
        # parser.add_argument("--order", type=int, default=3, help="order of Bessel function")
        # parser.add_argument("--output", default="plot.png", help="output image file")
        # args = parser.parse_args()

        # Compute maximum
        
        f = lambda x: -special.jv(3, x)
        sol = optimize.minimize(f, 1.0)

        # Plot
        x = np.linspace(0, 10, 5000)
        # plt.plot(x, special.jv(args.order, x), '-', sol.x, -sol.fun, 'o')

        plt.plot(x, special.jv(3, x), '-', sol.x, -sol.fun, 'o')
        rv_plot = StringIO.StringIO()
        # Produce output
        # plt.savefig(args.output, dpi=96)
        plt.title("SciPy PNG")
        plt.savefig(rv_plot, dpi=96, format="png")
        plt.clf()
        png_img = """<img src="data:image/png;base64,%s"/>""" % rv_plot.getvalue().encode("base64").strip()
        self.response.write("""<html><head/><body>""")
        self.response.write("Scipy")
        self.response.write(png_img)
        self.response.write("""</body> </html>""")

class setPhase(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('phase.html')
        self.response.out.write(template.render())

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

class imageHandler(webapp2.RequestHandler):
    def post(self):
        user_id = users.get_current_user().user_id() 
        ludo = SessionData.query(SessionData.user == user_id).get()
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

class handlePhase(webapp2.RequestHandler):
    def get(self):
        phaselist = self.request.get_all('phase')
        self.response.write("""<html><head/><body>""")
        logging.info(phaselist)
        self.response.write("""</body> </html>""")
    
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
            ludo = SessionData(user=user_id)
        ludo.sampleBlob = self.request.get('file')
        ludo.sampleFilename = self.request.params["file"].filename
        user_data_key = ludo.put()
        logging.debug(ludo.sampleFilename)
        logging.debug(user_data_key)
        res = dynamic_png(user_data_key)
        csv = user_data_key.urlsafe()
        template = JINJA_ENVIRONMENT.get_template('chart.html')
        template_vars = {
            'phaselist': ludo.phaselist,
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
    ('/profile',showProfile),
    ('/processImage',imageHandler),
    ('/img', renderImage),
    ('/phase', setPhase),
    ('/scipy', testscipy),
    ('/process', processFile),
    ('/savePhase', handlePhase),
    ('/upload_form', FileUploadFormHandler ),
    ('/', ShowHome),
], debug=True)

