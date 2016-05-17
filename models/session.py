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
    currentMode = ndb.KeyProperty() #current mode - if set use it
    
    # modes = ndb.KeyProperty(kind="QuantModeModel", repeated=True) - This does not have strong consistency... sigh

#     tutorialInstance = ndb.Key('Tutorial', int(tutID)).get()
# tutorialInstance.chapters.append(chap)

#  def create_tag(self):
#         # requires two writes
#         tag = Tag(name="my_tag")
#         tag.put()
#         self.tags.append(tag)
#         self.put()
