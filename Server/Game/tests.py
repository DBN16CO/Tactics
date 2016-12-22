from django.test import TestCase
from Game.models import Game_User, Game_Queue, Unit, Game
from Static.models import Version, Class
from User.models import Users
from Communication.testhelper import *
from Game.tasks import processMatchmakingQueue
import json

class TestUnit(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def helper_green_set_team_units(self):
		"""
		Helper class which creates a list of units to test with.

		The list will consist of one of each unit in the database, alphabetically.
		It will stop once the number needed for the specific version is reached.
		If there are less than the max number of units, it will then repeat the first unit
		"""
		version = Version.objects.latest('pk')
		all_units = Class.objects.filter()
		units = []
		count = 0

		for unit in all_units:
			units.append(str(unit.name))
			count += 1

			if count >= version.unit_count:
				break

		while len(units) < version.unit_count:
			units.append(str(all_units[0].name))

		return json.dumps(units)

	def helper_green_place_unit_units(self):
		unit_names = json.loads(self.helper_green_set_team_units())
		units_dict_list = []
		count = 0
		for name in unit_names:
			unit = {"Name":name,"X":count,"Y":0}
			units_dict_list.append(unit)

			count += 1

		return json.dumps(units_dict_list)

	def test01_set_team_bad_json_input(self):
		startTestLog("test01_set_team_bad_json_input")

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
		valid_unit_list = self.helper_green_set_team_units()
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
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Ability":"Extra Range"}')
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
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information is incomplete."}))

		# Test missing ability
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information is incomplete."}))

		# Test invalid leader
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"fake_leader","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information provided is invalid."}))

		# Test invalid ability
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Ability":"fake_ability","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The leader information provided is invalid."}))

		# Test invalid ability-leader pair
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Ability":"Steal","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The Sniper cannot use the ability Steal."}))

		# Test invaild unit name
		self.channel.send('{"Command":"ST","Units":[' + invalid_unit_name_str + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The following are not valid unit selections: " + str(invalid_unit_name_list)}))

		# Test invaild perk name
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Ability":"Extra Range","Perks":[' + invalid_perk_str + ']}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The following are not valid perk selections: " + str(invalid_perk_list)}))

		# Test too many perks selected
		self.channel.send('{"Command":"ST","Units":' + valid_unit_list + ',"Leader":"Sniper","Ability":"Extra Range","Perks":[' + too_many_perks + ']}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"Too many perks have been selected (4)."}))

		endTestLog("test01_set_team_bad_json_input")

	def test02_set_team_price_max_exceeded(self):
		startTestLog("test02_set_team_price_max_exceeded")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		too_expensive_team = ''
		for _ in range(version.unit_count):
			too_expensive_team += '"Armor",'
		too_expensive_team = too_expensive_team.strip(",")

		# Test that a user cannot exceed the price maximum
		self.channel.send('{"Command":"ST","Units":[' + too_expensive_team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[]}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False,"Error":"The selected team is 400 over the unit budget."}))

		endTestLog("test2_set_team_price_max_exceeded")

	def test03_set_team_valid_input(self):
		startTestLog("test03_set_team_valid_input")

		# Create user and login
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"set_team_user","password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		team = ''
		for _ in range(version.unit_count):
			team += '"Swordsman",'
		team = team.strip(",")
		perks = '"Extra Money", "Forest Fighter", "Mountain Fighter"'
		user = Users.objects.get(username="set_team_user")

		# Run command twice to ensure first run's DB entries are properly cleared
		for _ in range(2):
			# Test that the expected response was returned
			self.channel.send('{"Command":"ST","Units":[' + team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + perks + ']}')
			result = self.channel.receive()
			self.assertEqual(result, json.dumps({"Success":True,}))

			# Test that the values were added to the database
			self.assertEqual(Game_User.objects.filter(user=user).count(), 1)
			self.assertEqual(Unit.objects.filter(owner=user).count(), 8)

		endTestLog("test03_set_team_valid_input")

	def test04_find_match_before_set_team(self):
		startTestLog("test04_find_match_before_set_team")
		# Create user and login
		username = "set_team_user"
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":username,"password":"abc12345","email":"setTeam@email.com"}))

		# Call find match
		self.channel.send('{"Command":"FM"}')
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "You must set a team before starting a match.")

		# Ensure the user was not added to the game queue
		user = Users.objects.filter(username=username).first()
		game_queue_obj = Game_Queue.objects.filter(user=user).first()
		self.assertEqual(game_queue_obj, None)

		endTestLog("test04_find_match_before_set_team")

	def test05_find_match_success(self):
		startTestLog("test04_find_match_success")
		# Create user and login
		username = "set_team_user"
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":username,"password":"abc12345","email":"setTeam@email.com"}))

		# Setup values
		version = Version.objects.latest('pk')
		team = ''
		for _ in range(version.unit_count):
			team += '"Swordsman",'
		team = team.strip(",")
		perks = '"Extra Money", "Forest Fighter", "Mountain Fighter"'
		user = Users.objects.get(username="set_team_user")
		self.channel.send('{"Command":"ST","Units":[' + team + '],"Leader":"Sniper","Ability":"Extra Range","Perks":[' + perks + ']}')
		self.channel.receive()

		# Call find match
		self.channel.send('{"Command":"FM"}')
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], True)

		# Ensure the user was added to the game queue
		user = Users.objects.filter(username=username).first()
		game_queue_obj_count = Game_Queue.objects.filter(user=user).count()
		self.assertEqual(game_queue_obj_count, 1)
		self.assertEqual(user.game_queue.channel_name, u'Test')

		endTestLog("test04_find_match_success")

	def test06_matchmaking_queue_success(self):
		startTestLog("test06_matchmaking_queue_success")

		self.assertTrue(self.channel.createUserAndJoinQueue({"username": "first_user", "password": "12345", "email": "fplayer@a.com"}, self.helper_green_set_team_units(), 1))
		self.assertTrue(Game_Queue.objects.count() == 1)

		user1 = Users.objects.filter(username="first_user").first()

		self.assertTrue(self.channel.createUserAndJoinQueue({"username": "second_user", "password": "12345", "email": "splayer@a.com"}, self.helper_green_set_team_units(), 2))
		self.assertTrue(Game_Queue.objects.count() == 2)

		user2 = Users.objects.filter(username="second_user").first()

		queue = Game_Queue.objects.filter()
		version = Version.objects.latest('pk')
		game_users = Game_User.objects
		maps = Map.objects

		self.assertEquals(len(Unit.objects.filter(owner=user1, game=None)), version.unit_count)
		self.assertEquals(len(Unit.objects.filter(owner=user2, game=None)), version.unit_count)

		self.assertTrue(len(Game_User.objects.filter(game=None)) == 2)

		processMatchmakingQueue(queue, version, maps, game_users)

		self.assertTrue(len(Game_User.objects.filter(game=None)) == 0)
		self.assertEquals(Game_User.objects.filter(user=user1).first().name, "vs. second_user #1")
		self.assertEquals(Game_User.objects.filter(user=user2).first().name, "vs. first_user #1")

		self.assertEquals(len(Unit.objects.filter(owner=user1, game=None)), 0)
		self.assertEquals(len(Unit.objects.filter(owner=user2, game=None)), 0)

		self.assertTrue(Game.objects.count() == 1)
		self.assertTrue(Game_Queue.objects.count() == 0)

		endTestLog("test06_matchmaking_queue_success")

	def test07_place_units_bad_json(self):
		startTestLog("test07_place_units_bad_json")
		valid_unit_list = self.helper_green_set_team_units()

		# Create user and login
		username = "place_team_u1"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":"abc12345","email":"placeUnitsm@email.com"}, self.helper_green_set_team_units()))

		username2 = "place_unit_u2"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":"abc12345","email":"setTeam2@email.com"}, self.helper_green_set_team_units(), 2))

		queue = Game_Queue.objects.filter()
		version = Version.objects.latest('pk')
		game_users = Game_User.objects
		maps = Map.objects
		processMatchmakingQueue(queue, version, maps, game_users)

		# Missing Game
		self.channel.send('{"Command":"PU","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Internal Error: Game key missing.")

		# Missing Units
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1"}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Internal Error: Unit key missing.")

		# Invalid list count
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":{}}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Not enough units selected: (8) required, (0) chosen.")

		endTestLog("test07_place_units_bad_json")

	def test08_place_units_bad_game_name(self):
		startTestLog("test08_place_units_bad_game_name")
		valid_unit_list = self.helper_green_set_team_units()

		# Create user and login
		username = "place_team_u1"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":"abc12345","email":"placeUnitsm@email.com"}, self.helper_green_set_team_units()))

		username2 = "place_unit_u2"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":"abc12345","email":"setTeam2@email.com"}, self.helper_green_set_team_units(), 2))

		# Place units command
		self.channel.send('{"Command":"PU","Game":"bad_game_name","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Invalid game name (bad_game_name) for user " + username + ".")

		endTestLog("test8_place_units_bad_game_name")

	def test09_place_units_bad_team_list(self):
		startTestLog("test09_place_units_bad_team_list")
		version = Version.objects.latest('pk')
		invalid_unit_list = '['
		for i in range(0, version.unit_count):
			invalid_unit_list += '{"Name":"Archer","X":' + str(i) + ',"Y":0},'
		invalid_unit_list = invalid_unit_list.strip(",") + "]"
		invalid_placement_list = '['
		for i in range(0, version.unit_count):
			invalid_placement_list += '{"Name":"Archer","X":' + str(i) + ',"Y":8},'
		invalid_placement_list = invalid_placement_list.strip(",") + "]"

		# Create user and login
		username = "place_team_u1"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":"abc12345","email":"placeUnitsm@email.com"}, self.helper_green_set_team_units()))

		username2 = "place_unit_u2"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":"abc12345","email":"setTeam2@email.com"}, self.helper_green_set_team_units(), 2))

		queue = Game_Queue.objects.filter()
		version = Version.objects.latest('pk')
		game_users = Game_User.objects
		maps = Map.objects
		processMatchmakingQueue(queue, version, maps, game_users)

		# Invalid list of units
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + invalid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Can only place units selected for this game.")

		# Missing X or Y
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + self.helper_green_place_unit_units().replace("X", "Z") + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Internal Error: Missing X or Y.")

		# Invalid placement location
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + invalid_placement_list + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Location X:0 Y:8 is not a valid placement location for a unit.")

		endTestLog("test09_place_units_bad_team_list")

	def test10_place_units_success(self):
		startTestLog("test10_place_units_success")
		valid_unit_list = self.helper_green_place_unit_units()

		# Create user and login
		username = "place_team_u1"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":"abc12345","email":"placeUnitsm@email.com"}, self.helper_green_set_team_units()))
		user1 = Users.objects.filter(username=username).first()

		username2 = "place_unit_u2"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":"abc12345","email":"setTeam2@email.com"}, self.helper_green_set_team_units(), 2))

		queue = Game_Queue.objects.filter()
		version = Version.objects.latest('pk')
		game_users = Game_User.objects
		maps = Map.objects
		processMatchmakingQueue(queue, version, maps, game_users)
		game = Game.objects.latest('pk')

		# Place units command
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		self.assertEqual(result["Success"], True)
		units = Unit.objects.filter(owner=user1, game=game)
		for unit in units:
			self.assertNotEqual(unit.x_pos, -1)
			self.assertNotEqual(unit.y_pos, -1)
			self.assertNotEqual(unit.hp_remaining, 0)

		endTestLog("test10_place_units_success")