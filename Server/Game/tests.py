from django.test import TestCase
from Game.models import Unit
from Communication.testhelper import *
import json

class TestUnit(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test1_set_team_empty_unit(self):
		startTestLog("test1_set_team_empty_unit")
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		self.channel.send('{"Command":"ST"}')
		result = self.channel.receive()
		logging.debug(result)

		self.assertEqual(result, json.dumps({"Success":False,"Error":"There were no units selected in the team."}))

		endTestLog("test1_set_team_empty_unit")

"""
	def test_create_unit_archer(self):
		startTestLog("test_create_unit_archer")
		# Create a user to use for the tests
		self.channel.send('{"Command":"CU","username":"archerowner","pw":"12345","email":"archerowner@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
	def test_create_unit_archer_success(self):
		logging.debug("==== Starting create unit archer success test ====")


		result = self.channel.createTestUser({"username": "archerowner", "password": "12345", "email": "archerowner@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"token": result["Token"]})
		self.assertTrue(result["Success"])

		# Create the archer unit
		self.channel.send('{"Command":"UC","class":"Archer","v":"1.0"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True,"uid":Unit.objects.latest('pk').id}))
		endTestLog("test_create_unit_archer")
		"""