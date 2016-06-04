from google.appengine.api import images
from PIL import Image

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
