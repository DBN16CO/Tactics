from django.test import TestCase
from Communication.testhelper import *
from Communication.testutil import *
import json

class TestStatic(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_initial_load(self):
		startTestLog("test_initial_load")
		self.channel.send('{"Command":"IL"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
		endTestLog("test_initial_load")
