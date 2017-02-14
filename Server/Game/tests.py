from django.test import TestCase
from Game.models import Game_User, Game_Queue, Unit, Game
from Static.models import Version, Ability, Class, Leader, Leader_Ability, Perk, Stat, Unit_Stat
from User.models import Users
from Communication.testhelper import *
from Game.tasks import processMatchmakingQueue
import copy, json

class TestGame(TestCase):
	def setUp(self):
		self.testHelper = TestHelper(self._testMethodName)

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

	def tearDown(self):
		endTestLog(self._testMethodName)

	def helper_golden_path_set_team_units(self):
		"""
		Helper function which creates a list of units to test with.
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

			if count >= version.unit_max:
				break

		while len(units) < version.unit_min:
			units.append(str(all_units[0].name))

		return units

	def helper_golden_path_place_unit_units(self):
		"""
		Helper function which creates a list of units as well as their placement location to test with.
		The list will consist of one of each unit in the database, alphabetically.
		It will stop once the number needed for the specific version is reached.
		If there are less than the max number of units, it will then repeat the first unit
		For the placement location, they will start at (0,0) and increment the X value
		"""
		unit_names = json.loads(self.helper_golden_path_set_team_units())
		units_dict_list = []
		count = 0
		for name in unit_names:
			unit = {"Name":name,"X":count,"Y":0}
			units_dict_list.append(unit)

			count += 1

		return json.dumps(units_dict_list)

	def helper_execute_failure(self, command, message, channel_num=1):
		"""
		This method will execute the provided command (in channel 1), receive the response, 
		then ensure that the 'Success' returned is FALSE,
		and that the provided message matches the produced 'Error' message
		
		NOTE: The provided command a dictionary that will need to be converted to a string here
		"""
		self.testHelper.send(json.dumps(command), channel_num)
		result = json.loads(self.testHelper.receive(channel_num))

		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], message)

	def helper_execute_success(self, command, channel_num=1):
		"""
		This method will execute the provided command (in channel 1), receive the response,
		ensure that the 'Success' is returned TRUE,
		and then return the result for further testing
		"""
		self.testHelper.send(json.dumps(command), channel_num)
		result = json.loads(self.testHelper.receive(channel_num))

		self.assertTrue(result["Success"])
		return result

class CommonSetupThroughFM(TestGame):
	"""
	The functions included within this class are useful for getting the test user up through
	being put into a matchmaking queue.

	The classes that inherit this functionality include:\n
		- TestSetTeam
		- TestFindMatch
		- TestMatchmaking
	"""
	def setUp(self):
		super(CommonSetupThroughFM, self).setUp()

		self.assertTrue(self.testHelper.createUserAndLogin(self.credentials))
		self.user = Users.objects.filter(username=self.credentials["username"]).first()

		# Generate the expected successful Set Team dictionary
		self.st_cmd = {
			"Command" : "ST",
			"Ability" : "Extra Range",
			"Leader"  : "Sniper",
			"Perks"   : [],							# None are required, just the key
			"Units"   : self.helper_golden_path_set_team_units()
		}

		self.fm_cmd = {"Command":"FM"}
		self.cs_cmd = {"Command":"CS"}

class TestSetTeam(CommonSetupThroughFM):
	"""
	All tests within this class relate specifically to the command 'ST' (Set team)

	It tests the following:\n
	- Each of the keys are included in the command: Ability, Leader, Perks, Units (Test 01)\n
	- The value for each key is a valid input - no 'fake_unit' (Test 01)\n
	- The ability-leader combination is valid (Test 01)\n
	- The maximum number of perks has not been exceeded (Test 01)\n
	- The limit for the minimum number have units has been met (Test 01)\n
	- The maximum number of units has not been exceeded (Test 01)\n
	- Creating a team that is over budget fails (Test 02)\n
	- Cannot select more than one of the same tier perk (Test 03)\n
	- Successfully calling the command returns 'Success'=True and: (Test 03)\n
		+ Sets the correct leader and ability to the game_user table\n
		+ Sets each tier perk correctly in the game_user table\n
		+ Sets the correct number and correct set of units to the unit table
	- Recalling the ST command resets the user's team (Test 03)

	"""
	def test_st_01_bad_json(self):
		# Test missing ability
		no_ability_cmd = copy.deepcopy(self.st_cmd)
		no_ability_cmd.pop("Ability", None)
		self.helper_execute_failure(no_ability_cmd, "The leader information is incomplete.")

		# Test missing leader
		no_leader_cmd = copy.deepcopy(self.st_cmd)
		no_leader_cmd.pop("Leader", None)
		self.helper_execute_failure(no_leader_cmd, "The leader information is incomplete.")	

		# Test missing perks
		no_perks_cmd = copy.deepcopy(self.st_cmd)
		no_perks_cmd.pop("Perks", None)
		self.helper_execute_failure(no_perks_cmd, "The perk information is incomplete.")

		# Test missing units
		no_units_cmd = copy.deepcopy(self.st_cmd)
		no_units_cmd.pop("Units", None)
		self.helper_execute_failure(no_units_cmd, "The unit information is incomplete.")

		# Test invalid ability
		bad_ability_cmd = copy.deepcopy(self.st_cmd)
		bad_ability_cmd["Ability"] = "fake_ability"
		self.helper_execute_failure(bad_ability_cmd, "The leader information provided is invalid.")

		# Test invalid leader
		bad_leader_cmd = copy.deepcopy(self.st_cmd)
		bad_leader_cmd["Leader"] = "fake_leader"
		self.helper_execute_failure(bad_leader_cmd, "The leader information provided is invalid.")

		# Test invaild perk name
		fake_perk_cmd = copy.deepcopy(self.st_cmd)
		fake_perk_cmd["Perks"] = ["fake_perk"]
		self.helper_execute_failure(fake_perk_cmd,
			"The following are not valid perk selections: fake_perk")
		
		# Test invaild unit name
		fake_units_cmd = copy.deepcopy(self.st_cmd)
		fake_units_cmd["Units"][0] = "fake_unit0"
		fake_units_cmd["Units"][1] = "fake_unit1"
		self.helper_execute_failure(fake_units_cmd,
			"The following are not valid unit selections: fake_unit0,fake_unit1")
		
		# Test invalid ability-leader pair
		bad_ldr_abil_cmd = copy.deepcopy(self.st_cmd)
		bad_ldr_abil_cmd["Ability"] = "Steal"
		self.helper_execute_failure(bad_ldr_abil_cmd, "The Sniper cannot use the ability Steal.")

		# Test too many perks selected
		extra_perks_cmd = copy.deepcopy(self.st_cmd)
		extra_perks_cmd["Perks"] = ["Extra Money", "Forest Fighter", "Mountain Fighter","Strong Arrows"]
		self.helper_execute_failure(extra_perks_cmd, "Too many perks have been selected (4).")

		# Test too few units selected
		empty_units_cmd = copy.deepcopy(self.st_cmd)
		empty_units_cmd["Units"] = []
		self.helper_execute_failure(empty_units_cmd,
			"You must select at least {0} unit(s), none chosen.".format(self.version.unit_min))

		# Test too many units selected
		extra_units_cmd = copy.deepcopy(self.st_cmd)
		while len(extra_units_cmd["Units"]) <= self.version.unit_max:
			extra_units_cmd["Units"].append("Archer")
		self.helper_execute_failure(extra_units_cmd, "Too many units have been selected (11).")

	def test_st_02_price_max_exceeded(self):
		# Create a team full of most expensive unit
		too_expensive_team = []
		for _ in range(self.version.unit_max):
			too_expensive_team.append("Armor")

		# Test that a user cannot exceed the price maximum
		self.st_cmd["Units"] = too_expensive_team
		self.helper_execute_failure(self.st_cmd, "The selected team is 1000 over the unit budget.")

	def test_st_03_multiple_same_tier_perks(self):
		# Select two tier 1 perks
		perks = ["Forest Fighter", "Mountain Fighter"]
		self.st_cmd["Perks"] = perks

		# Test that the expected response was returned
		self.helper_execute_failure(self.st_cmd,
			"Cannot select more than one tier 1 perk: Forest Fighter, Mountain Fighter")

	def test_st_04_valid_input(self):
		# Ensure the perk logic also runs
		perks = ["Extra Money", "Strong Arrows", "Mountain Fighter"]
		self.st_cmd["Perks"] = perks

		# Get the static DB values for  inputted team
		db_ability = Ability.objects.filter(name=self.st_cmd["Ability"],
			version=self.version).first()
		db_leader = Leader.objects.filter(name=self.st_cmd["Leader"],
			version=self.version).first()
		db_ldr_abil = Leader_Ability.objects.filter(leader=db_leader, ability=db_ability,
			version=self.version).first()
		db_t1_perk = Perk.objects.filter(tier=1, version=self.version).first()
		db_t2_perk = Perk.objects.filter(tier=2, version=self.version).first()
		db_t3_perk = Perk.objects.filter(tier=3, version=self.version).first()

		# Run command twice to ensure first run's DB entries are properly cleared
		for _ in range(2):
			# Test that the expected response was returned
			self.helper_execute_success(self.st_cmd)

			# Test that the values were added to the database
			# Game_User: Ability, Leader, Perks
			game_user_qs = Game_User.objects.filter(user=self.user)
			self.assertEqual(game_user_qs.count(), 1)	# If > 1, first run's values not cleared
			game_user = game_user_qs.first()
			self.assertEqual(game_user.leader_abil, db_ldr_abil)
			self.assertEqual(game_user.perk_1.name, db_t1_perk.name)
			self.assertEqual(game_user.perk_2.name, db_t2_perk.name)
			self.assertEqual(game_user.perk_3.name, db_t3_perk.name)

			# Units
			unit_qs = Unit.objects.filter(owner=self.user)
			self.assertEqual(unit_qs.count(), len(self.st_cmd["Units"]))
			unit_list = []
			for unit in unit_qs:
				unit_list.append(unit.unit_class.name)
			self.assertEqual(sorted(unit_list), sorted(self.st_cmd["Units"]))

class TestFindMatch(CommonSetupThroughFM):
	"""
	All tests within this class related specifically to the commands:
		'FM' (Find Match)
		'CS' (Cancel Search)

	It tests the following:\n
	- A user cannot call FM before ST, and: (Test 01)\n
		+ If they attempt to do so, they will not be added to the game queue\n
	- Calling FM after setting the team returns success as well as: (Test 02)\n
		+ Adds that user to the game queue, with their correct channel name
	- Calling CS after a successful FM returns Success and removes the user from the queue (Test 03)\n
	- Calling CS when not in queue still returns success (Test 03)
	"""
	def test_fm_01_before_set_team(self):
		self.helper_execute_failure(self.fm_cmd,
			"You must set a team before starting a match.")

		# Ensure the user was not added to the game queue
		game_queue_obj = Game_Queue.objects.filter(user=self.user).first()
		self.assertEqual(game_queue_obj, None)

	def test_fm_02_find_match_success(self):
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)

		# Ensure the user was added to the game queue
		game_queue_obj_qs = Game_Queue.objects.filter(user=self.user)
		self.assertEqual(game_queue_obj_qs.count(), 1)
		self.assertEqual(game_queue_obj_qs.first().user, self.user)
		self.assertEqual(game_queue_obj_qs.first().channel_name, u'Test')

	def test_fm_03_cancel_search_success(self):
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)

		self.assertTrue(Game_Queue.objects.count() == 1)

		# Test Cancel Game Search succeeds
		self.helper_execute_success(self.cs_cmd)
		self.assertTrue(Game_Queue.objects.count() == 0)

		# Test Cancel Game Search succeeds even when user isn't in the queue
		self.helper_execute_success(self.cs_cmd)

class TestMatchmaking(CommonSetupThroughFM):
	"""
	All tests within this class relate specifically to the matchmaking logic.

	Specifically, the following is tested:\n
	- When two players are matched: (Test 01)\n
		+ They are each removed from the Game Queue\n
		+ They are each added as Game Users as a pair\n
		+ Their Game User name includes the other player's name and the game count between them\n
		+ A game object was created for them\n
		+ Each of their units was added to the game\n
	"""
	def setUp(self):
		super(TestMatchmaking, self).setUp()

		# Finish putting user 1 into the queue
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)

		# Create user 2 and put him into the queue
		self.assertTrue(self.testHelper.createUserAndLogin(self.credentials2, 2))
		self.user2 = Users.objects.filter(username=self.credentials2["username"]).first()
		self.helper_execute_success(self.st_cmd, 2)
		self.helper_execute_success(self.fm_cmd, 2)

		# Ensure that there are two players in the queue at this point
		self.assertTrue(Game_User.objects.filter(game=None).count() == 2)

	def test_mm_01_pair_success(self):
		processMatchmakingQueue()

		# Ensure the Game_User objects were created properly
		self.assertTrue(len(Game_User.objects.filter(game=None)) == 0)
		self.assertEquals(Game_User.objects.filter(user=self.user).first().name, "vs. game_user_2 #1")
		self.assertEquals(Game_User.objects.filter(user=self.user).first().team, 1)
		self.assertEquals(Game_User.objects.filter(user=self.user2).first().name, "vs. game_user_1 #1")
		self.assertEquals(Game_User.objects.filter(user=self.user2).first().team, 2)

		# Ensure all of each player's units were assigned to the game
		self.assertEquals(len(Unit.objects.filter(owner=self.user, game=None)), 0)
		self.assertEquals(len(Unit.objects.filter(owner=self.user2, game=None)), 0)

		# Ensure that a game was created
		self.assertTrue(Game.objects.count() == 1)

		# Ensure that the Game Queue is now empty
		self.assertTrue(Game_Queue.objects.count() == 0)

class TestPlaceUnits(TestGame):
	def test07_place_units_bad_json(self):
		startTestLog("test07_place_units_bad_json")
		valid_unit_list = self.helper_golden_path_set_team_units()

		# Create user and login
		username = "place_team_u1_bj"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":self.channel.generateValidPassword(),"email":"placeUnitsm@email.com"}, self.helper_golden_path_set_team_units()))

		username2 = "place_unit_u2_bj"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":self.channel.generateValidPassword(),"email":"setTeam2@email.com"}, self.helper_golden_path_set_team_units(), 2))

		processMatchmakingQueue()

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
		self.assertEqual(result["Error"], "Incorrect number of units selected: (8) required, (0) chosen.")

		endTestLog("test07_place_units_bad_json")

	def test08_place_units_bad_game_name(self):
		startTestLog("test08_place_units_bad_game_name")
		valid_unit_list = self.helper_golden_path_set_team_units()

		# Create user and login
		username = "pu_u1_bgn"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":self.channel.generateValidPassword(),"email":"placeUnitsm@email.com"}, self.helper_golden_path_set_team_units()))

		username2 = "pu_u2_bgn"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":self.channel.generateValidPassword(),"email":"setTeam2@email.com"}, self.helper_golden_path_set_team_units(), 2))

		# Place units command
		self.channel.send('{"Command":"PU","Game":"bad_game_name","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Invalid game name (bad_game_name) for user " + username + ".")

		endTestLog("test08_place_units_bad_game_name")

	def test09_place_units_bad_team_list(self):
		startTestLog("test09_place_units_bad_team_list")
		version = Version.objects.latest('pk')

		# Create user and login
		username = "pu_u1_btl"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":self.channel.generateValidPassword(),"email":"placeUnitsm@email.com"}, self.helper_golden_path_set_team_units()))

		username2 = "pu_u2_btl"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":self.channel.generateValidPassword(),"email":"setTeam2@email.com"}, self.helper_golden_path_set_team_units(), 2))

		processMatchmakingQueue()

		user = Users.objects.filter(username=username).first()
		unit_count = Unit.objects.filter(owner=user).count()

		invalid_unit_list = '['
		for i in range(0, unit_count):
			invalid_unit_list += '{"Name":"Archer","X":' + str(i) + ',"Y":0},'
		invalid_unit_list = invalid_unit_list.strip(",") + "]"
		invalid_placement_list = '['
		for i in range(0, unit_count):
			invalid_placement_list += '{"Name":"Archer","X":' + str(i) + ',"Y":8},'
		invalid_placement_list = invalid_placement_list.strip(",") + "]"

		# Invalid list of units
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + invalid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Can only place units selected for this game.")

		# Missing X or Y
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + self.helper_golden_path_place_unit_units().replace("X", "Z") + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Internal Error: Missing X or Y.")

		# Invalid placement location
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + invalid_placement_list + '}', 1)
		result = json.loads(self.channel.receive())
		self.assertEqual(result["Success"], False)
		self.assertEqual(result["Error"], "Location X:0 Y:8 is not a valid placement location for a unit for your team.")

		endTestLog("test09_place_units_bad_team_list")

	def test10_place_units_success(self):
		startTestLog("test10_place_units_success")
		valid_unit_list = self.helper_golden_path_place_unit_units()

		# Create user and login
		username = "place_team_u1"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":self.channel.generateValidPassword(),"email":"placeUnitsm@email.com"}, self.helper_golden_path_set_team_units()))
		user1 = Users.objects.filter(username=username).first()

		username2 = "place_unit_u2"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":self.channel.generateValidPassword(),"email":"setTeam2@email.com"}, self.helper_golden_path_set_team_units(), 2))

		processMatchmakingQueue()
		game = Game.objects.latest('pk')

		# Place units command
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		self.assertEqual(result["Success"], True)
		units = Unit.objects.filter(owner=user1, game=game)
		for unit in units:
			self.assertNotEqual(unit.x, -1)
			self.assertNotEqual(unit.y, -1)
			self.assertNotEqual(unit.hp, 0)
			self.assertFalse(unit.acted)

		endTestLog("test10_place_units_success")

	def test11_query_games_user_success(self):
		startTestLog("test11_query_games_user_success")

		self.assertTrue(self.channel.createUsersAndMatch({"username": "first_user", "password": self.channel.generateValidPassword(), "email": "fplayer@a.com"}, 
			self.helper_golden_path_set_team_units(), {"username": "second_user", "password": self.channel.generateValidPassword(), "email": "splayer@a.com"},
			self.helper_golden_path_set_team_units()))
		self.channel.send('{"Command":"QGU"}')
		result = json.loads(self.channel.receive())

		user1 = Users.objects.filter(username="first_user").first()
		user2 = Users.objects.filter(username="second_user").first()

		self.assertTrue(result["Success"])
		self.assertTrue(len(result["Games"]) == 1)
		self.assertEquals(result["Games"][0]["Name"], Game_User.objects.filter(user=user1).first().name)
		self.assertEquals(result["Games"][0]["Round"], Game.objects.filter().first().game_round)

		endTestLog("test11_query_games_user_success")

	def test12_take_action_bad_json(self):
		startTestLog("test12_take_action_bad_json")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get unit in location 0,0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":1,"Y":1}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Test a missing game key
		missing_game_command = copy.deepcopy(valid_wait_command)
		del missing_game_command["Game"]
		self.channel.send(json.dumps(missing_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Game Key missing.")

		# Test an invalid game key value
		bad_game_command = copy.deepcopy(valid_wait_command)
		bad_game_command["Game"] = "fake_game_name" 		# Just bad game name
		self.channel.send(json.dumps(bad_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "No match for game of name fake_game_name.")
		bad_game_command["Game"] = "vs. first_user #1" 		# Existing, but bad name
		self.channel.send(json.dumps(bad_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "No match for game of name vs. first_user #1.")

		# Test action key missing
		missing_action_command = copy.deepcopy(valid_wait_command)
		del missing_action_command["Action"]
		self.channel.send(json.dumps(missing_action_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Action Key missing.")

		# Test an invalid action key value
		fake_action_command = copy.deepcopy(valid_wait_command)
		fake_action_command["Action"] = "fake_action"
		self.channel.send(json.dumps(fake_action_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "The selected action is not valid.")

		# Test an invalid action for the specific unit
		bad_action_command = copy.deepcopy(valid_wait_command)
		bad_action_command["Action"] = "Attack"
		self.channel.send(json.dumps(bad_action_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "The selected action is not valid.")

		# Location information missing
		missing_x_command = copy.deepcopy(valid_wait_command)
		del missing_x_command["X"]
		self.channel.send(json.dumps(missing_x_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: New location information incomplete.")
		missing_y_command = copy.deepcopy(valid_wait_command)
		del missing_y_command["Y"]
		self.channel.send(json.dumps(missing_y_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: New location information incomplete.")

		# Test unit key missing
		missing_unit_command = copy.deepcopy(valid_wait_command)
		del missing_unit_command["Unit"]
		self.channel.send(json.dumps(missing_unit_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Unit Key missing.")

		# Test an invalid unit key value
		bad_unit_command = copy.deepcopy(valid_wait_command)
		bad_unit_command["Unit"] = -1
		self.channel.send(json.dumps(bad_unit_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Specified unit ID not in game.")

		# Test target key missing
		missing_target_command = copy.deepcopy(valid_wait_command)
		missing_target_command["Action"] = "Heal"
		self.channel.send(json.dumps(missing_target_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Target Key missing.")
		logging.debug(result)

		# Test target key invalid unit
		bad_target_command = copy.deepcopy(valid_wait_command)
		bad_target_command["Action"] = "Heal"
		bad_target_command["Target"] = -1
		self.channel.send(json.dumps(bad_target_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Specified target ID not in game.")
		logging.debug(result)

		endTestLog("test12_take_action_bad_json")

	def test13_take_action_invalid_move(self):
		startTestLog("test13_take_action_invalid_move")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":1,"Y":1}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Moving onto ally unit
		ally_move_command = copy.deepcopy(valid_wait_command)
		ally_move_command["Y"] = 0
		self.channel.send(json.dumps(ally_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Location (1,0) occupied by an ally. Can move through, but not to, that token.")

		# Move near enemy for next tests
		unit.x = 0
		unit.y = 14
		unit.save()

		# Moving onto enemy unit
		ally_move_command = copy.deepcopy(valid_wait_command)
		ally_move_command["Y"] = 15
		self.channel.send(json.dumps(ally_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Location (1,15) occupied by an enemy. Cannot move to that token.")

		# Move enemy in way of target path
		enemy_unit = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()
		enemy_unit.x = 3
		enemy_unit.y = 14
		enemy_unit.save()

		# Moving through enemy unit
		move_through_enemy_command = copy.deepcopy(valid_wait_command)
		move_through_enemy_command["X"] = 7
		move_through_enemy_command["Y"] = 14
		self.channel.send(json.dumps(move_through_enemy_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Target location (7,14) was out of reach for Flier at location (0,14).")

		# Ensure on map with forest
		version = Version.objects.latest('pk')
		game = Game.objects.latest('pk')
		map_obj = Map.objects.filter(version=version, name="Forest Pattern").first()
		game.map_path = map_obj
		game.save()

		# Move the swordsman to a place to test forest movement
		sword = Unit.objects.filter(game=game_users.first().game, x=7, y=0).first()
		sword.x = 1
		sword.y = 5
		sword.save()

		# Forest impedes full movement
		move_through_forest_command = copy.deepcopy(valid_wait_command)
		move_through_forest_command["Unit"] = sword.id
		move_through_forest_command["X"] = 1
		move_through_forest_command["Y"] = 8
		self.channel.send(json.dumps(move_through_forest_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Target location (1,8) was out of reach for Swordsman at location (1,5).")

		endTestLog("test13_take_action_invalid_move")

	def test14_take_action_move_on_self_success(self):
		startTestLog("test14_take_action_move_on_self_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get flier in location 0,0
		newX = 0
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)

		# Ensure the same unit cannot act again this turn
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That unit has already acted this turn.")

		endTestLog("test14_take_action_move_on_self_success")

	def test15_take_action_valid_move_success(self):
		startTestLog("test15_take_action_valid_move_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0
		newX = 2
		newY = 3
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Moving south full distance
		valid_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(valid_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)

		endTestLog("test15_take_action_valid_move_success")

	def test15a_take_action_full_move_success(self):
		startTestLog("test15a_take_action_full_move_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0
		newX = 2
		newY = 8
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Moving south full distance
		valid_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(valid_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)

		endTestLog("test15a_take_action_full_move_success")

	def test16_take_action_valid_move_through_ally_success(self):
		startTestLog("test16_take_action_valid_move_through_ally_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(x=2, y=0).first()	# Get flier in location 2,0
		newX = 10
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Moving through an ally unit
		valid_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(valid_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)

		endTestLog("test16_take_action_valid_move_through_ally_success")

	def test17_take_action_before_enemy_placement(self):
		startTestLog("test17_take_action_before_enemy_placement")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		self.channel.createUsersAndMatch(credentials1, team1, credentials2, team2)
		# Place units command
		valid_unit_list = self.helper_golden_path_place_unit_units()
		self.channel.send('{"Command":"PU","Game":"vs. ' + credentials2["username"] + ' #1","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		unit = Unit.objects.filter(x=0, y=0).first()	# Get flier in location 0,0
		newX = 8
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Call take action before the opponent has placed their units
		self.channel.send(json.dumps(valid_wait_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Please wait until your opponent places their units before taking a turn.")

		endTestLog("test17_take_action_before_enemy_placement")

	def test18_take_action_before_placement(self):
		startTestLog("test18_take_action_before_placement")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Hack to undo placing units
		units = Unit.objects.filter(owner=game_users.first().user, game=game_users.first().game)
		for unit in units:
			unit.x = -1
			unit.y = -1
			unit.save()

		unit = Unit.objects.filter(x=-1, y=-1).first()	# Get flier in location 0,0
		newX = 8
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Wait", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY}

		# Call take action before you have placed your units
		self.channel.send(json.dumps(valid_wait_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "You must place all of your units before taking a turn.")

		endTestLog("test18_take_action_before_placement")

	def test19_place_units_not_matched(self):
		startTestLog("test19_place_units_not_matched")
		valid_unit_list = self.helper_golden_path_place_unit_units()

		# Create user and login
		username = "place_team_u1_nm"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username,"password":self.channel.generateValidPassword(),"email":"placeUnitsm@email.com"}, self.helper_golden_path_set_team_units()))
		user1 = Users.objects.filter(username=username).first()

		username2 = "place_unit_u2_nm"
		self.assertTrue(self.channel.createUserAndJoinQueue(
			{"username":username2,"password":self.channel.generateValidPassword(),"email":"setTeam2@email.com"}, self.helper_golden_path_set_team_units(), 2))

		processMatchmakingQueue()
		game = Game.objects.latest('pk')

		# Set team again to 0 to emulate placing units without a team side
		game_user_1 = Game_User.objects.filter(user=user1).first()
		game_user_1.team = 0
		game_user_1.save()

		# Place units command
		self.channel.send('{"Command":"PU","Game":"vs. ' + username2 + ' #1","Units":' + valid_unit_list + '}', 1)
		result = json.loads(self.channel.receive())

		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "You cannot place units until both players have set their teams.")

		endTestLog("test19_place_units_not_matched")

	def test20_take_action_basic_attack_success(self):
		startTestLog("test20_take_action_basic_attack_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = -5
		unit_luck.save()

		# Ensure the attacker cannot miss
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = 15
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 1,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=15).first()
		oldTgtHp = tgt.hp

		newX = 1
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		# Target had a: Normal Hit      Critical Hit    Missed
		self.assertTrue(unit.hp == 8 or unit.hp == 4 or unit.hp == 10)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 9)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertTrue(result["Unit"]["NewHP"] == 8 or result["Unit"]["NewHP"] == 4 or result["Unit"]["NewHP"] == 10)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 10)
		self.assertEqual(result["Target"]["NewHP"], 9)


		endTestLog("test20_take_action_basic_attack_success")

	def test21_take_action_bad_heal(self):
		startTestLog("test21_take_action_bad_heal")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get healer in location 0,0
		valid_wait_command = {"Command":"TA", "Action":"Heal", "Game":"vs. second_user #1", "Unit":unit.id, "X":1,"Y":1}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Trying to heal self
		bad_heal_self_command = copy.deepcopy(valid_wait_command)
		bad_heal_self_command["Target"] = unit.id
		self.channel.send(json.dumps(bad_heal_self_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Cannot target self.")
		logging.debug(result)

		# Trying to heal ally at full health
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()	# Get target in location 1,0
		bad_heal_ally_command = copy.deepcopy(valid_wait_command)
		bad_heal_ally_command["Target"] = tgt.id
		self.channel.send(json.dumps(bad_heal_ally_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Target already has full Health.")
		logging.debug(result)

		# Trying to heal ally that is dead
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()	# Get target in location 1,0
		tgt.hp = 0
		tgt.save()
		bad_heal_dead_ally_command = copy.deepcopy(valid_wait_command)
		bad_heal_dead_ally_command["Target"] = tgt.id
		self.channel.send(json.dumps(bad_heal_dead_ally_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "You cannot heal dead units.")
		logging.debug(result)

		# Trying to heal target too far away
		tgt = Unit.objects.filter(game=game_users.first().game, x=3, y=0).first()	# Get target in location 1,0
		bad_heal_far_ally_command = copy.deepcopy(valid_wait_command)
		bad_heal_far_ally_command["Target"] = tgt.id
		self.channel.send(json.dumps(bad_heal_far_ally_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Must be within 2 range.  Target is 3 away.")
		logging.debug(result)

		# Trying to heal the enemy
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()	# Get target in location 1,0
		unit.y = 13
		unit.save()
		bad_heal_enemy_command = copy.deepcopy(valid_wait_command)
		bad_heal_enemy_command["Target"] = tgt.id
		bad_heal_enemy_command["Y"] = 14
		self.channel.send(json.dumps(bad_heal_enemy_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Cannot heal the enemy units!")
		logging.debug(result)

		endTestLog("test21_take_action_bad_heal")

	def test22_take_action_bad_attack(self):
		startTestLog("test22_take_action_bad_attack")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()	# Get attacker in location 1,0
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":1,"Y":1}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Trying to attack self
		bad_attack_self_command = copy.deepcopy(valid_wait_command)
		bad_attack_self_command["Target"] = unit.id
		self.channel.send(json.dumps(bad_attack_self_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Cannot target self.")
		logging.debug(result)

		# Trying to attack an ally
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get target in location 0,0
		bad_attack_ally_command = copy.deepcopy(valid_wait_command)
		bad_attack_ally_command["Target"] = tgt.id
		self.channel.send(json.dumps(bad_attack_ally_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Cannot attack your own units!")
		logging.debug(result)

		# Move unit close to enemy for attacks
		unit.y = 13
		unit.save()

		# Trying to attack target too far away
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()	# Get target in location 1,0
		bad_attack_far_enemy_command = copy.deepcopy(valid_wait_command)
		bad_attack_far_enemy_command["Target"] = tgt.id
		bad_attack_far_enemy_command["Y"] = 13
		self.channel.send(json.dumps(bad_attack_far_enemy_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Must be within 2 range.  Target is 3 away.")
		logging.debug(result)

		# Trying to attack an enemy that is dead
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=15).first()	# Get target in location 1,0
		tgt.hp = 0
		tgt.save()
		bad_attack_dead_enemy_command = copy.deepcopy(valid_wait_command)
		bad_attack_dead_enemy_command["Target"] = tgt.id
		bad_attack_dead_enemy_command["Y"] = 13
		self.channel.send(json.dumps(bad_attack_dead_enemy_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "You cannot attack dead units.")
		logging.debug(result)

		endTestLog("test22_take_action_bad_attack")

	def test23_take_action_crit_attack_success(self):
		startTestLog("test23_take_action_crit_attack_success")

		# NOTE: Also tests that the dead target cannot counter 

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = 100
		unit_luck.save()

		# Ensure the attacker cannot miss
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = 15
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 0,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()	# Get flier in location 2,0
		oldTgtHp = tgt.hp

		newX = 0
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 10)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 0)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertEqual(result["Unit"]["NewHP"], 10)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 5)
		self.assertEqual(result["Target"]["NewHP"], 0)

		endTestLog("test23_take_action_crit_attack_success")

	def test24_take_action_attack_no_counter_success(self):
		startTestLog("test24_take_action_attack_no_counter_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()	# Get archer in location 1,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = -1
		unit_luck.save()

		# Ensure the attacker cannot miss
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = 10
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 5,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=5, y=15).first()
		oldTgtHp = tgt.hp

		newX = 4
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving right 4 (outside target counter range)
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 10)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 18)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertEqual(result["Unit"]["NewHP"], 10)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 20)
		self.assertEqual(result["Target"]["NewHP"], 18)

		endTestLog("test24_take_action_attack_no_counter_success")

	def test25_take_action_attack_miss_success(self):
		startTestLog("test25_take_action_attack_miss_success")

		# NOTE: Also tests that target can counter (and crit)

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit (and guarantee counter is a crit)
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = -100
		unit_luck.save()

		# Ensure the attacker always misses
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = -100
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 5,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=3, y=15).first()
		oldTgtHp = tgt.hp

		newX = 3
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Move into attack range
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 3)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 20)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertEqual(result["Unit"]["NewHP"], 3)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 20)
		self.assertEqual(result["Target"]["NewHP"], 20)

		endTestLog("test25_take_action_attack_miss_success")

	def test25b_take_action_tgt_passive_success(self):
		startTestLog("test25b_take_action_tgt_passive_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit (and guarantee counter is a crit)
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = -100
		unit_luck.save()

		# Ensure the attacker always misses
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = -100
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 5,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()
		oldTgtHp = tgt.hp

		newX = 0
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving right 4 (outside target counter range)
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 10)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 5)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertEqual(result["Unit"]["NewHP"], 10)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 5)
		self.assertEqual(result["Target"]["NewHP"], 5)

		endTestLog("test25b_take_action_tgt_passive_success")

	def test25a_take_action_counter_misses_success(self):
		startTestLog("test25a_take_action_counter_misses_success")

		# NOTE: Also tests that target can counter

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=2, y=0).first()	# Get flier in location 2,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Ensure the attacker cannot crit (and guarantee counter is a crit)
		version = Version.objects.latest('pk')
		clss = unit.unit_class
		luck = Stat.objects.filter(name="Luck", version=version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first()
		unit_luck.value = -100
		unit_luck.save()

		# Ensure the attacker never misses
		agil = Stat.objects.filter(name="Agility", version=version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=clss, version=version).first()
		unit_agil.value = 100
		unit_agil.save()

		# Move unit near target
		unit.y = 14
		unit.save()
		oldHp = unit.hp

		# Get target at location 5,15
		tgt = Unit.objects.filter(game=game_users.first().game, x=0, y=15).first()
		oldTgtHp = tgt.hp

		newX = 0
		newY = 14
		valid_wait_command = {"Command":"TA", "Action":"Attack", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving right 4 (outside target counter range)
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 10)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 3)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 10)
		self.assertEqual(result["Unit"]["NewHP"], 10)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 5)
		self.assertEqual(result["Target"]["NewHP"], 3)

		endTestLog("test25a_take_action_counter_misses_success")

	def test26_take_action_heal_fully_success(self):
		startTestLog("test26_take_action_heal_fully_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get cleric in location 0,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Get target at location 1,0
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()

		# Simulate target losing 1 health
		oldTgtHp = tgt.hp
		tgt.hp = oldTgtHp - 1
		tgt.save()

		newX = 0
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Heal", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 5)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, oldTgtHp)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 5)
		self.assertEqual(result["Unit"]["NewHP"], 5)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], oldTgtHp-1)
		self.assertEqual(result["Target"]["NewHP"], oldTgtHp)

		endTestLog("test26_take_action_heal_fully_success")

	def test27_take_action_heal_partial_success(self):
		startTestLog("test27_take_action_heal_partial_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get cleric in location 0,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Get target at location 1,0
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()

		# Simulate target losing all but 1 health
		oldTgtHp = tgt.hp
		tgt.hp = 1
		tgt.save()

		newX = 0
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Heal", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 5)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 5)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 5)
		self.assertEqual(result["Unit"]["NewHP"], 5)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 1)
		self.assertEqual(result["Target"]["NewHP"], 5)

		endTestLog("test27_take_action_heal_partial_success")

	def test28_take_action_heal_exact_full_success(self):
		startTestLog("test28_take_action_heal_exact_full_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		unit = Unit.objects.filter(game=game_users.first().game, x=0, y=0).first()	# Get cleric in location 0,0

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Get target at location 1,0
		tgt = Unit.objects.filter(game=game_users.first().game, x=1, y=0).first()

		# Simulate target losing all but 1 health
		oldTgtHp = tgt.hp
		tgt.hp = 6
		tgt.save()

		newX = 0
		newY = 0
		valid_wait_command = {"Command":"TA", "Action":"Heal", "Game":"vs. second_user #1", "Unit":unit.id, "X":newX,"Y":newY, "Target":tgt.id}

		# Moving onto self
		self_move_command = copy.deepcopy(valid_wait_command)
		self.channel.send(json.dumps(self_move_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])
		unit = Unit.objects.filter(pk=unit.id).first()
		self.assertEqual(unit.x, newX)
		self.assertEqual(unit.y, newY)
		self.assertEqual(unit.hp, 5)
		tgt = Unit.objects.filter(pk=tgt.id).first()
		self.assertEqual(tgt.hp, 10)

		self.assertTrue(result["Success"])
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], unit.id)
		self.assertEqual(result["Unit"]["HP"], 5)
		self.assertEqual(result["Unit"]["NewHP"], 5)
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["HP"], 6)
		self.assertEqual(result["Target"]["NewHP"], 10)

		endTestLog("test28_take_action_heal_exact_full_success")

	def test29_end_turn_bad_json(self):
		startTestLog("test29_end_turn_bad_json")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		valid_wait_command = {"Command":"ET", "Game":"vs. second_user #1"}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Test a missing game key
		missing_game_command = copy.deepcopy(valid_wait_command)
		del missing_game_command["Game"]
		self.channel.send(json.dumps(missing_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Internal Error: Game Key missing.")

		# Test an invalid game key value
		bad_game_command = copy.deepcopy(valid_wait_command)
		bad_game_command["Game"] = "fake_game_name" 		# Just bad game name
		self.channel.send(json.dumps(bad_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "No match for game of name fake_game_name.")
		bad_game_command["Game"] = "vs. first_user #1" 		# Existing, but bad name
		self.channel.send(json.dumps(bad_game_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "No match for game of name vs. first_user #1.")

		endTestLog("test29_end_turn_bad_json")

	def test30_end_turn_not_turn(self):
		startTestLog("test30_end_turn_not_turn")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		valid_wait_command = {"Command":"ET", "Game":"vs. second_user #1"}

		# Ensure it is player 2's turn
		game = game_users.first().game
		user2 = Users.objects.filter(username=credentials2["username"]).first()
		game.user_turn = user2
		game.save()
		
		self.channel.send(json.dumps(valid_wait_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == False)
		self.assertEqual(result["Error"], "Please wait until it is your turn.")

		endTestLog("test30_end_turn_not_turn")

	def test31_end_turn_success(self):
		startTestLog("test31_end_turn_success")

		# Setup command
		credentials1 = {"username":"first_user","password":self.channel.generateValidPassword(),"email":"p1@email.com"}
		credentials2 = {"username":"second_user","password":self.channel.generateValidPassword(),"email":"p2@email.com"}
		team1 = self.helper_golden_path_set_team_units()
		team2 = self.helper_golden_path_set_team_units()
		game_users = self.channel.createUsersAndPlaceUnits(credentials1, team1, credentials2, team2)
		self.assertTrue(len(game_users) == 2)
		valid_wait_command = {"Command":"ET", "Game":"vs. second_user #1"}

		# Ensure it is player 1's turn
		game = game_users.first().game
		user1 = Users.objects.filter(username=credentials1["username"]).first()
		game.user_turn = user1
		game.save()

		# Simulate all units on other player's team having moved
		user2 = Users.objects.filter(username=credentials2["username"]).first()
		Unit.objects.filter(owner=user2, game=game).update(acted=True)
		
		self.channel.send(json.dumps(valid_wait_command))
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"] == True)

		game = Game.objects.latest('pk')
		self.assertEqual(game.user_turn, user2)
		units = Unit.objects.filter(owner=user2, game=game).exclude(hp__lte=0)
		for unit in units:
			self.assertFalse(unit.acted)

		endTestLog("test31_end_turn_success")