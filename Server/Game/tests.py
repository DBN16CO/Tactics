from django.test import TestCase
from Game.models import Game_User, Unit
from Static.models import Version
from Communication.testhelper import *
import json

class TestUnit(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test1_set_team_bad_json_input(self):
		startTestLog("test1_set_team_bad_json_input")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		too_many_units = ''
		for _ in range(version.unit_count+1):
			too_many_units += '"Archer",'
		too_many_units =too_many_units.strip(",")
		valid_unit_list = ''
		for _ in range(version.unit_count):
			valid_unit_list += '"Archer",'
		valid_unit_list = valid_unit_list.strip(",")
		invalid_unit_name_list = ''
		invalid_unit_name_str  = ''
		for _ in range(version.unit_count):
			invalid_unit_name_list += "fake_unit,"
			invalid_unit_name_str += '"fake_unit",'
		invalid_unit_name_list = invalid_unit_name_list.strip(",")
		invalid_unit_name_str = invalid_unit_name_str.strip(",")
		invalid_perk_list = ''
		invalid_perk_str = ''
		for _ in range(3):
			invalid_perk_list += "fake_perk,"
			invalid_perk_str += '"fake_perk",'
		invalid_perk_list = invalid_perk_list.strip(",")
		invalid_perk_str = invalid_perk_str.strip(",")
		valid_perk_list = '"Extra Money", "Forest Fighter", "Mountain Fighter"'
		too_many_perks = valid_perk_list + ', "Strong Arrows"'

		# Test no units
		self.channel.send('{"Command":"ST","Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The unit information is incomplete."}))

		# Test no perks
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Ability":"Extra Range"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The perk information is incomplete."}))

		# Test too few units selected
		self.channel.send('{"Command":"ST","Units":["Archer"],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"You must select "
			+ str(version.unit_count) + " units, only 1 chosen."}))

		# Test too many units selected
		self.channel.send('{"Command":"ST","Units":[' + too_many_units + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"Too many units have been selected (9)."}))

		# Test missing leader
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information is incomplete."}))

		# Test missing ability
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information is incomplete."}))

		# Test invalid leader
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"fake_leader","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information provided is invalid."}))

		# Test invalid ability
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Ability":"fake_ability","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information provided is invalid."}))

		# Test invalid ability-leader pair
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Ability":"Steal","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The Sniper cannot use the ability Steal."}))

		endTestLog("test1_set_team_bad_json_input")

		# Test invaild unit name
		self.channel.send('{"Command":"ST","Units":[' + invalid_unit_name_str + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The following are not valid unit selections: " + str(invalid_unit_name_list)}))

		# Test invaild perk name
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + invalid_perk_str + ']}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The following are not valid perk selections: " + str(invalid_perk_list)}))

		# Test too many perks selected
		self.channel.send('{"Command":"ST","Units":[' + valid_unit_list + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + too_many_perks + ']}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"Too many perks have been selected (4)."}))

		endTestLog("test1_set_team_bad_json_input")

	def test2_set_team_price_max_exceeded(self):
		startTestLog("test2_set_team_price_max_exceeded")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		too_expensive_team = ''
		for i in range(version.unit_count):
			too_expensive_team += '"Armor",'
		too_expensive_team = too_expensive_team.strip(",")

		# Test that a user cannot exceed the price maximum
		self.channel.send('{"Command":"ST","Units":[' + too_expensive_team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The selected team is 1400 over the unit budget."}))

		endTestLog("test2_set_team_price_max_exceeded")

	def test3_set_team_valid_input(self):
		startTestLog("test2_set_team_valid_input")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		team = ''
		for i in range(version.unit_count):
			team += '"Swordsman",'
		team = team.strip(",")
		perks = '"Extra Money", "Forest Fighter", "Mountain Fighter"'
		user = Users.objects.get(username="set_team_user")

		# Run command twice to ensure first run's DB entries are properly cleared
		for i in range(2):
			# Test that the expected response was returned
			self.channel.send('{"Command":"ST","Units":[' + team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + perks + ']}')
			result = self.channel.receive()
			self.assertEqual(result, json.dumps({"Success":True,}))

			# Test that the values were added to the database
			self.assertEqual(Game_User.objects.filter(user=user).count(), 1)
			self.assertEqual(Unit.objects.filter(owner=user).count(), 8)

		endTestLog("test2_set_team_valid_input")

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