from django.test import TestCase
from router import *
from testhelper import *
import json

class TestCommunication(TestCase):
	def setUp(self):
		"""
		Sets up all Communication tests
		"""
		self.channel = TestHelper()

	def test1_ping_server(self):
		"""
		Tests that the ping-pong logic works
		"""
		startTestLog("test1_ping_server")

		self.channel.send('{"PING":"PING"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"PONG":"PONG"}))

		endTestLog("test1_ping_server")

	def test2_internal_error(self):
		startTestLog("test2_internal_error")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"bad_cmd_usr","password":"abc12345","email":"bcu@email.com"}))

		self.channel.send('{"Command":"fake_command"}')
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Server Error.")

		endTestLog("test2_internal_error")