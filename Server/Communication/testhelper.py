"""
.. module:: testhelper
   :synopsis: Helps with the testing in all of the other apps

.. moduleauthor:: Drew, Brennan, and Nick
"""
from channels import Channel
from channels.tests import ChannelTestCase
from router import *
from Server.config import *
from Game.models import Unit
import Static.create_data

class TestHelper(ChannelTestCase):
	"""
	Used to set up any unit tests
	"""
	def __init__(self):
		"""
		Sets up the test config and initializes the Database
		"""
		self.channel = Channel(u'Test')
		self.setupConfig()
		self.initStaticData("1.0")

	def setupConfig(self):
		"""
		Sets up necessary configuration for each unit test
		"""
		startup()

	def send(self, payload):
		"""
		Sends the provided payload input to the router
		"""
		self.channel.send({u'bytes': payload, u'reply_channel': u'Test'})
		message = self.get_next_message(u'Test', require=True)
		processRequest(message)

	def receive(self):
		"""
		Receives the router response to a command
		"""
		result = self.get_next_message(u'Test', require=True)
		return result.content['text']

	def createTestUser(self, credentials):
		"""
		Creates a user for commands that require a user for the test
		"""
		request = {"Command": "CU", "username": credentials["username"], "pw": credentials["password"], "email": credentials["email"]}
		self.send(json.dumps(request))
		result = json.loads(self.receive())

		return result

	def login(self, credentials):
		"""
		Logs in a user with the provided credentials
		"""
		request = {"Command": "LGN"}
		if "username" in credentials and "password" in credentials:
			request["username"] = credentials["username"]
			request["pw"] = credentials["password"]
		elif "token" in credentials:
			request["token"] = credentials["token"]

		self.send(json.dumps(request))
		result = json.loads(self.receive())

		return result

	def createUserAndLogin(self, credentials):
		"""
		Creates a user for testing and logs them in
		"""
		request = {}

		if "username" in credentials and "password" in credentials and "email" in credentials:
			request["username"] = credentials["username"]
			request["password"] = credentials["password"]
			request["email"]    = credentials["email"]
		else:
			logging.error("Credentials was missing valid info:"
				+ "\n\tUsername:" + credentials["username"]
				+ "\n\tPassword:" + credentials["password"]
				+ "\n\tEmail:   " + credentials["email"])
			return False

		result = self.createTestUser(request)
		if result["Success"] == False:
			logging.error("Creating the test user resulted in failure:\n\t" + result["Error"])
			return False

		result = self.login(request)
		if result["Success"] == False:
			logging.error("Logging in test user resulted in failure:\n\t" + result["Error"])
	
		return result["Success"]

	@staticmethod
	def initStaticData(version_name):
		"""
		Initializes all data in the Static app that may be needed for testing
		"""
		result = Static.create_data.setup_static_db(version_name)
		if result == False:
			logging.error("Problem occurred setting up database.")

		return False


def startTestLog(testName):
	"""
	Provides all header messages to the log for any test
	"""
	logging.debug("")
	logging.debug("==========  Starting Test: " + str(testName) + " ==========")

def endTestLog(testName):
	"""
	Provides all footer messages to the log for any test

	Note: Will not run if any test fails at some point
	"""
	logging.debug("========== Finishing Test: " + str(testName) + " ==========")