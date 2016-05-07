#Where business logics reside.
from google.appengine.ext import ndb
from google.appengine.api import users

import logging

from models.session import SessionData

class QuantModeModel(ndb.Model):
        selected = ndb.PickleProperty()
        available = ndb.PickleProperty()
        qlambda = ndb.FloatProperty()
        qtarget = ndb.StringProperty()
        fwhma = ndb.FloatProperty()
        fwhmb = ndb.FloatProperty()

class CompanyModel (ndb.Model):
        name = ndb.StringProperty()

class QuantMode(object):
        def whoami(self):
                logging.info("I am a QuantMode instance")        
        def save_mode (self,qname,qtarget,qlambda,a,b,input_id):
		#id will be greater than zero when EDIT action is triggered.
		if id>0:
                        user_id = users.get_current_user().user_id()
                        session = SessionData.query(SessionData.user == user_id).get()
                        user_data_key = session.key
                        #get ID of entity Key
                        qmode_key = ndb.Key(QuantModeModel, input_id, parent=session.key)
                        qmode = qmode_key.get()

                        # qmode = QuantModeModel.get_by_id(id)
                        # qmode_key = ndb.Key(urlsafe=id)
                        # qmode_key = ndb.Key('QuantModeModel', id)
                        # qmode = qmode_key.get()
                        # logging.debug(qmode)
                        
#                        qmode = ndb.Key(urlsafe=qmode_key).get()

                        # member2 = QuantModeModel.get_by_id(id)
                        # qmode_key = ndb.Key(QuantModeModel, id)
                        # qmode = qmode_key.get()
		else:
#			company = CompanyModel(id='RedRock',name='RedRock Enterprise')
			# company = CompanyModel(name='RedRock Enterprise')
			# company.put()

                        # Get session data instance
                        user = users.get_current_user()
                        user_id = users.get_current_user().user_id()
                        user_id = users.get_current_user().user_id()
                        logging.debug(user_id)
                        session = SessionData.query(SessionData.user == user_id).get()
                        user_data_key = session.key
                        
                        # Get session data instance key
			qmode = QuantModeModel(id=qname, parent=session.key)

		qmode.qlambda = qlambda
		qmode.qtarget = qtarget
		qmode.fwhma = a
		qmode.fwhmb = b
                #		qmode.user_name = users.get_current_user().email()
		qmode.put()

	def delete_mode (self, mode_ids):
		if len(mode_ids)>0:
			for mode_id in mode_ids:
				qmode_k = ndb.Key('CompanyModel','RedRock','QuantModeModel',long(employee_id))
				qmode = db.get(qmode_k)
				db.delete(qmode_k)

	def list_mode (self):
                user = users.get_current_user()
                user_id = users.get_current_user().user_id()
                user_id = users.get_current_user().user_id()
                logging.debug(user_id)
                session = SessionData.query(SessionData.user == user_id).get()
                user_data_key = session.key
                
                logging.debug("Not sure")
		mode_query = QuantModeModel.query()
                logging.debug(mode_query)
                mode_query = QuantModeModel.query(ancestor=session.key)
		return mode_query
        
