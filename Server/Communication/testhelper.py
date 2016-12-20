"""
.. module:: testhelper
   :synopsis: Helps with the testing in all of the other apps

.. moduleauthor:: Drew, Brennan, and Nick
"""
from channels import Channel
from channels.tests import ChannelTestCase
from router import *
from Server.config import *
from Game.models import Unit, Game, Game_User, Game_Queue
from Static.models import Map
import Static.create_data
from Game.tasks import processMatchmakingQueue

class TestHelper(ChannelTestCase):
	"""
	Used to set up any unit tests
	"""
	def __init__(self):
		"""
		Sets up the test config and initializes the Database
		"""
		self.channel = Channel(u'Test')
		self.channel2 = Channel(u'Test2')
		self.setupConfig()
		self.initStaticData("1.0")

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
		logging.error("Chn.name="+chn.name)
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
			logging.error("Creating the test user resulted in failure:\n\t" + result["Error"])
			return False

		result = self.login(request, channel_num)
		if result["Success"] == False:
			logging.error("Logging in test user resulted in failure:\n\t" + result["Error"])
	
		return result["Success"]

	def createUserAndJoinQueue(self, credentials, channel_num=1):
		self.createUserAndLogin(credentials, channel_num)

		username = credentials["username"]

		# Setup values and set team
		version = Version.objects.latest('pk')
		team = ''
		for _ in range(version.unit_count):
			team += '"Swordsman",'
		team = team.strip(",")
		perks = '"Extra Money", "Forest Fighter", "Mountain Fighter"'
		user = Users.objects.get(username=username)
		self.send('{"Command":"ST","Units":[' + team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + perks + ']}', channel_num)
		self.receive(channel_num)

		# Find a match
		self.send('{"Command":"FM"}', channel_num)
		result = json.loads(self.receive(channel_num))

		return result["Success"]

	def createUsersAndMatch(self, credentials1, credentials2):
		self.createUserAndJoinQueue(credentials1, 1)
		self.createUserAndJoinQueue(credentials2, 2)

		queue = Game_Queue.objects.filter()
		version = Version.objects.latest('pk')
		game_users = Game_User.objects
		maps = Map.objects

		processMatchmakingQueue(queue, version, maps, game_users)

		return Game_User.objects.filter(user=Users.objects.filter(username=credentials1["username"])).first().game != None

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