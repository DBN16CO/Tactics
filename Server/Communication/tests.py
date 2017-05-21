from testhelper import *
from router import *
import json
import Game.maphelper
from Static.models import Version

class TestCommunication(CommonTestHelper):
	"""
	Tests the following:
	- Pinging the server returns pong (Test 01)\n
	- Sending in a fake command returns an error message (Test 02)\n
	- Sending in a request with no command returns a message (Test 03)
	- Sending a command with invlid JSON will return an error message (Test 04)\n
	- Sending a command without being authenticated will return an error message (Test 05)\n
	- When the map data is empty for a version it is reloaded successfully (Test 06)\n
	"""
	def test_cm_01_ping_server(self):
		self.testHelper.send('{"PING":"PING"}')
		result = self.testHelper.receive()
		self.assertEqual(result, json.dumps({"PONG":"PONG"}))

	def test_cm_02_internal_error(self):
		# Create user and login
		self.assertTrue(self.testHelper.createUserAndLogin(
			{"username":"bad_cmd_usr","password":self.testHelper.generateValidPassword(),"email":"bcu@email.com"}))

		cmd = {"Command":"fake_command"}
		self.helper_execute_failure(cmd, "Invalid command.")

	def test_cm_03_missing_command(self):
		self.helper_execute_failure({}, "The command information is incomplete.")

	def test_cm_04_invalid_json(self):
		self.testHelper.send({}, 1)
		result = json.loads(self.testHelper.receive(1))

		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "Input JSON invalid.")

	def test_cm_05_unauthenthicated_access(self):
		self.helper_execute_failure({"Command":"AAA"}, "User is not authenticated, please login.")

	def test_cm_06_reload_static_maps(self):
		Game.maphelper.maps = {}

class TestReceivedMessage(CommonTestHelper):
	"""
	Tests the following:
	- \n
	"""
	def setUp(self):
		super(TestReceivedMessage, self).setUp()

		self.version = Version.objects.latest('pk')

		# Credentials for user 1
		self.credentials = {
			"username" : "game_user_1",
			"password" : self.testHelper.generateValidPassword(),
			"email"    : "userOne@email.com"
		}

		# Credentials for user 2
		self.credentials2 = {
			"username" : "game_user_2",
			"password" : self.testHelper.generateValidPassword(),
			"email"    : "userTwo@email.com"
		}

		self.assertTrue(self.testHelper.createUserAndLogin(self.credentials))
		self.user = Users.objects.filter(username=self.credentials["username"]).first()

		# Generate the expected successful Set Team dictionary
		self.st_cmd = {
			"Command" : "ST",
			"Ability" : "Extra Range",
			"Leader"  : "Sniper",
			"Perks"   : [],							# None are required, just the key
			"Units"   : self.create_valid_team_list()
		}

		self.fm_cmd = {"Command":"FM"}
		self.cs_cmd = {"Command":"CS"}

	def test_rm_01_received_message_success(self):
		pass
