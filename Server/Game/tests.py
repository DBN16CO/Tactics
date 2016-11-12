from django.test import TestCase
from Game.models import Unit
from Communication.testhelper import *
import json

class TestUnit(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_create_unit_archer(self):
		# Create a user to use for the tests
		self.channel.send('{"Command":"CU","username":"archerowner","pw":"12345","email":"archerowner@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))

		# Create the archer unit
		self.channel.send('{"Command":"UC","class":"Archer","owner":"archerowner","v":"1.0"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True,"uid":Unit.objects.latest('pk').id}))