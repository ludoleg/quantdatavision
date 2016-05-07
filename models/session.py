from google.appengine.ext import ndb

class SessionData(ndb.Model):
    user = ndb.StringProperty()
    email = ndb.StringProperty()
    selected = ndb.PickleProperty()
    available = ndb.PickleProperty()
    results = ndb.PickleProperty()
    avatar = ndb.BlobProperty()
    sampleFilename = ndb.StringProperty()
    sampleBlob = ndb.BlobProperty()
    qlambda = ndb.FloatProperty()
    qtarget = ndb.StringProperty()
    fwhma = ndb.FloatProperty()
    fwhmb = ndb.FloatProperty()
#     modes = ndb.StructuredProperty(Mode, repeated=True)
