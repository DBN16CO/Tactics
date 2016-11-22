from channels import Channel
from channels.tests import ChannelTestCase
from router import *
from Server.config import *
from Static.models import Version, Action, Class, Hero_Ability, Leader, Map, Perk, Stat, Terrain
from Game.models import Unit
import Static.create_data

class TestHelper(ChannelTestCase):
	def __init__(self):
		self.channel = Channel(u'Test')
		self.setupConfig()
		self.initStaticData()

	def setupConfig(self):
		startup()

	def send(self, payload):
		self.channel.send({u'bytes': payload, u'reply_channel': u'Test'})
		message = self.get_next_message(u'Test', require=True)
		processRequest(message)

	def receive(self):
		result = self.get_next_message(u'Test', require=True)
		return result.content['text']

	def createTestUser(self, credentials):
		request = {"Command": "CU", "username": credentials["username"], "pw": credentials["password"], "email": credentials["email"]}
		self.send(json.dumps(request))
		result = json.loads(self.receive())

		return result

	def login(self, credentials):
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

	def initStaticData(self):
		version = "1.0"
		result = Static.create_data.setup_static_db(version)
		if result == False:
			logging.error("Problem occurred setting up database.")

		return False
		



def startTestLog(testName):
	logging.debug("")
	logging.debug("==========  Starting Test: " + str(testName) + " ==========")

def endTestLog(testName):
	logging.debug("========== Finishing Test: " + str(testName) + " ==========")