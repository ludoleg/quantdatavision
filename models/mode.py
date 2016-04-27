from google.appengine.ext import ndb

class Mode(ndb.Model):
    selected = ndb.PickleProperty()
    available = ndb.PickleProperty()
    qlambda = ndb.FloatProperty()
    qtarget = ndb.StringProperty()
    fwhma = ndb.FloatProperty()
    fwhmb = ndb.FloatProperty()
