#Where business logics reside.
from google.appengine.ext import ndb
from google.appengine.api import users

import logging
import phaselist

from models.session import SessionData

class QuantModeModel(ndb.Model):
        title = ndb.StringProperty(default="default")
        selected = ndb.PickleProperty(default=phaselist.defaultPhases)
        available = ndb.PickleProperty(default=phaselist.availablePhases)
        qlambda = ndb.FloatProperty(default=0)
        qtarget = ndb.StringProperty(default="Co")
        fwhma = ndb.FloatProperty(default=-0.001348)
        fwhmb = ndb.FloatProperty(default=0.352021)
        inventory = ndb.StringProperty(default="cement")

class QuantMode(object):
        def whoami(self):
                logging.info("I am a QuantMode instance")        
        def save_mode (self,qname,qtarget,qlambda,a,b,inventory,input_id):
		#id will be greater than zero when EDIT action is triggered.
                user_id = users.get_current_user().user_id()
		if input_id>0:
                        session = SessionData.query(SessionData.user == user_id).get()
                        user_data_key = session.key
                        #get ID of entity Key
                        qmode = ndb.Key(QuantModeModel, input_id, parent=session.key).get()

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
                        logging.debug(user_id)
                        session = SessionData.query(SessionData.user == user_id).get()
                        user_data_key = session.key
                        
                        # Get session data instance key
	       	        qmode = QuantModeModel(title=qname, parent=session.key)

		qmode.qlambda = qlambda
		qmode.qtarget = qtarget
		qmode.fwhma = a
		qmode.fwhmb = b
                qmode.inventory = inventory
                
                #		qmode.user_name = users.get_current_user().email()
		key = qmode.put()

                session.currentMode = key
                session.put()

	def delete_mode (self, mode_ids):
                logging.debug("Delete Mode")
		if len(mode_ids)>0:
                        user_id = users.get_current_user().user_id() 
                        session = SessionData.query(SessionData.user == user_id).get()

			for mode_id in mode_ids:
                                logging.debug(mode_id)
                                # qmode_k = ndb.Key(urlsafe=mode_key)
			        qmode_k = ndb.Key('QuantModeModel', int(mode_id), parent=session.key)
                                logging.debug(qmode_k)
                                # if qmode_k in session.modes:
                                #         idx = session.modes.index(qmode_k)
                                #         del session.modes[idx]
                                #         session.put()

				qmode = qmode_k.get()
                                logging.debug(qmode)
                                qmode_k.delete()
	def list_mode (self):
                user = users.get_current_user()
                user_id = users.get_current_user().user_id()
                logging.debug(user_id)
                session = SessionData.query(SessionData.user == user_id).get()
                logging.debug("List Mode")
                logging.debug(session)
                
                user_data_key = session.key
                
		mode_query = QuantModeModel.query()
                logging.debug(mode_query)
                mode_query = QuantModeModel.query(ancestor=session.key)
		return mode_query

        # Used in different schema, ie repeated keyproperty - had to change because of strong consistency issues.
                # list_of_modes = ndb.get_multi(session.modes)
                # for m in list_of_modes:
                #        logging.debug(m)
		# return list_of_modes
