"""
.. module:: testhelper
   :synopsis: Helps with the testing in all of the other apps

.. moduleauthor:: Drew, Brennan, and Nick
"""
from channels import Channel
from channels.tests import ChannelTestCase
from django.test import TestCase
from router import *
from Server.config import *
from Game.models import Unit, Game, Game_User, Game_Queue
from Game.maphelper import *
from Static.models import Map
import Static.create_data
from Game.tasks import processMatchmakingQueue
from Server import config
import Static.statichelper

class TestHelper(ChannelTestCase):
	"""
	Used to set up any unit tests
	"""
	def __init__(self, testName=None):
		"""
		Sets up the test config and initializes the Database
		"""
		# Logging
		self.setupConfig()
		startTestLog(testName)

		# Test Channels
		self.channel = Channel(u'Test')
		self.channel2 = Channel(u'Test2')

		# Create database, with version 1.0 data
		self.initStaticData("1.0")

		# Load all of the map data for the most-recent version
		loadMaps()

	def setupConfig(self):
		"""
		Sets up necessary configuration for each unit test
		"""
		startup()

	def send(self, payload, channel_num=1):
		"""
		Sends the provided payload input to the router
		"""
		if channel_num == 1:
			chn = self.channel
		elif channel_num == 2:
			chn = self.channel2

		chn.send({u'bytes': payload, u'reply_channel': chn.name})
		logging.debug("Chn.name={0}".format(chn.name))
		message = self.get_next_message(chn.name, require=True)
		processRequest(message)

	def receive(self, channel_num=1):
		"""
		Receives the router response to a command
		"""
		if channel_num == 1:
			chn = self.channel
		elif channel_num == 2:
			chn = self.channel2

		result = self.get_next_message(chn.name, require=True)
		return result.content['text']

	def generateValidPassword(self):
		"""
		Generates the same valid password based on the configured password policy
		"""
		password = ''

		requirements = config.PASSWORD_POLICY["Requirements"]
		for req in requirements:
			req_enabled, req_list = requirements[req]
			if req_enabled:
				password += req_list[0]

		for _ in range(len(password), config.PASSWORD_POLICY['Min Length']):
			password += 'a'

		return password

	def createTestUser(self, credentials, channel_num=1):
		"""
		Creates a user for commands that require a user for the test
		"""
		request = {"Command": "CU", "username": credentials["username"], "pw": credentials["password"], "email": credentials["email"]}
		logging.debug(json.dumps(request))
		self.send(json.dumps(request), channel_num)
		result = json.loads(self.receive(channel_num))
		logging.debug(json.dumps(result))

		return result

	def login(self, credentials, channel_num=1):
		"""
		Logs in a user with the provided credentials
		"""
		request = {"Command": "LGN"}
		if "username" in credentials and "password" in credentials:
			request["username"] = credentials["username"]
			request["pw"] = credentials["password"]
		elif "token" in credentials:
			request["token"] = credentials["token"]

		self.send(json.dumps(request), channel_num)
		result = json.loads(self.receive(channel_num))

		return result

	def createUserAndLogin(self, credentials, channel_num=1):
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

		result = self.createTestUser(request, channel_num)
		if result["Success"] == False:
			logging.error("Creating the test user resulted in failure:\n\t{0}".format(result["Error"]))
			return False

		result = self.login(request, channel_num)
		if result["Success"] == False:
			logging.error("Logging in test user resulted in failure:\n\t{0}".format(result["Error"]))
	
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
	logging.debug("============  Starting Test: {0} ============".format(testName))

def endTestLog(testName):
	"""
	Provides all footer messages to the log for any test
	"""
	logging.debug("============ Finishing Test: {0} ============".format(testName))

class CommonTestHelper(TestCase):
	"""
	Contains methods common to all test classes
	"""
	def setUp(self):
		self.testHelper = TestHelper(self._testMethodName)

		# Clear the cached static DB data since IDs change between tests
		Static.statichelper.static_data = {}

	def tearDown(self):
		endTestLog(self._testMethodName)

	def helper_execute_failure(self, command, message, channel_num=1):
		"""
		This method will execute the provided command (in channel 1), receive the response, 
		then ensure that the 'Success' returned is FALSE,
		and that the provided message matches the produced 'Error' message
		
		NOTE: The provided command a dictionary that will need to be converted to a string here
		"""
		self.testHelper.send(json.dumps(command), channel_num)
		result = json.loads(self.testHelper.receive(channel_num))

		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], message)

	def helper_execute_success(self, command, channel_num=1):
		"""
		This method will execute the provided command (in channel 1), receive the response,
		ensure that the 'Success' is returned TRUE,
		and then return the result for further testing
		"""
		self.testHelper.send(json.dumps(command), channel_num)
		result = json.loads(self.testHelper.receive(channel_num))

		self.assertTrue(result["Success"])
		return result