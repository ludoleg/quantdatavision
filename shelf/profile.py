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

        
