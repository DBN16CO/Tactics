from django.test import TestCase
from router import *
from testhelper import *
import json

class TestCommunication(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_ping_server(self):
		self.channel.send('{"PING":"PING"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"PONG":"PONG"}))