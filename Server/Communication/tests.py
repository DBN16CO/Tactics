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

	def test_ping_server(self):
		"""
		Tests that the ping-pong logic works
		"""
		startTestLog("test_ping_server")

		self.channel.send('{"PING":"PING"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"PONG":"PONG"}))

		endTestLog("test_ping_server")