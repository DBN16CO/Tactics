from testhelper import *
from router import *
import json

class TestCommunication(CommonTestHelper):
	"""
	Tests the following:
	- Pinging the server returns pong (Test 01)\n
	- Sending in a fake command returns an error message (Test 02)\n
	- Sending in a request with no command returns a message (Test 03)
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
		self.helper_execute_failure(cmd, "Internal Server Error.")

	def test_cm_03_missing_command(self):
		self.helper_execute_failure({}, "The command information is incomplete.")