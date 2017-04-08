from Game.models import Game_User, Game_Queue, Unit, Game
from Static.models import Version, Ability, Class, Leader, Leader_Ability, Perk, Stat, Unit_Stat
from User.models import Users
from Communication.testhelper import *
from Game.tasks import processMatchmakingQueue
import copy, json, math
import Static.statichelper

class TestGame(Communication.testhelper.CommonTestHelper):
	def setUp(self):
		super(TestGame, self).setUp()

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

		self.assertTrue(self.testHelper.createUserAndLogin(self.credentials))
		self.user = Users.objects.filter(username=self.credentials["username"]).first()

		# Generate the expected successful Set Team dictionary
		self.st_cmd = {
			"Command" : "ST",
			"Ability" : "Extra Range",
			"Leader"  : "Sniper",
			"Perks"   : [],							# None are required, just the key
			"Units"   : self.create_valid_team_list()
		}

		self.fm_cmd = {"Command":"FM"}
		self.cs_cmd = {"Command":"CS"}

		self.pu_cmd = {
			"Command" : "PU",
			"Game"    : "vs. {0} #1".format(self.credentials2["username"]),
			"Units"   : self.place_valid_team_dict(self.st_cmd["Units"])
		}

	def create_valid_team_list(self):
		"""
		Creates a list of units to test with.
		The list will consist of one of each unit in the database.
		It will stop once the maximum 
		number needed for the specific version is reached.
		If there are less than the min number of units, it will then repeat the first unit
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

	def place_valid_team_dict(self, units, team=1):
		"""
		Creates a list of dictionaries of units as well as their placement location to test with.
		Sorts the inputted list of units and places them horizontally across the
		top or bottom of the map, depending on the user's team.
		"""
		units_dict_list = []

		y = 0 if team == 1 else 15
		count = 0
		for unit in sorted(units):
			unit_dict = {"Name":unit, "X":count,"Y":y}
			units_dict_list.append(unit_dict)

			count += 1

		return units_dict_list

	def get_both_users_in_queue(self):
		"""
		Puts both users into the game queue 
		"""
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

class TestSetTeam(TestGame):
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
	- Recalling the ST command resets the user's team (Test 03)\n
	- Successfully calling the function returns a success and updates the DB properly (Test 04)\n
	- Rerunning ST replaces the DB with the new team (Test 05)\n
	- Rerunning ST with an error does not alter the DB (Test 05)\n
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
		self.helper_execute_failure(bad_ability_cmd,
			"The {0} cannot use the ability {1}.".format(bad_ability_cmd["Leader"], bad_ability_cmd["Ability"]))

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

		# Test that the expected response was returned
		self.helper_execute_success(self.st_cmd)

		# Get the static DB values for inputted team
		db_ability = Ability.objects.filter(name=self.st_cmd["Ability"],
			version=self.version).first()
		db_leader = Leader.objects.filter(name=self.st_cmd["Leader"],
			version=self.version).first()
		db_ldr_abil = Leader_Ability.objects.filter(leader=db_leader, ability=db_ability,
			version=self.version).first()
		db_t1_perk = Perk.objects.filter(tier=1, version=self.version).first()
		db_t2_perk = Perk.objects.filter(tier=2, version=self.version).first()
		db_t3_perk = Perk.objects.filter(tier=3, version=self.version).first()

		# Test that the values were added to the database
		# Game_User: Ability, Leader, Perks
		game_user = Game_User.objects.filter(user=self.user).first()

		self.assertEqual(game_user.perk_1.name, db_t1_perk.name)
		self.assertEqual(game_user.perk_2.name, db_t2_perk.name)
		self.assertEqual(game_user.perk_3.name, db_t3_perk.name)
		self.assertEqual(game_user.leader_abil, db_ldr_abil)

		# Units
		unit_qs = Unit.objects.filter(owner=self.user)
		self.assertEqual(unit_qs.count(), len(self.st_cmd["Units"]))
		unit_list = []
		for unit in unit_qs:
			unit_list.append(unit.unit_class.name)
		self.assertEqual(sorted(unit_list), sorted(self.st_cmd["Units"]))

	def test_st_05_repeat_command(self):
		# Call command once, should succeed
		self.helper_execute_success(self.st_cmd)

		# Change the units submitted
		new_unit_list = []
		for _ in range(0, self.version.unit_min):
			new_unit_list.append("Archer")
		self.st_cmd["Units"] = new_unit_list

		# Rerun command, should only have archer now
		self.helper_execute_success(self.st_cmd)

		unit_qs = Unit.objects.filter(owner=self.user)

		self.assertEqual(unit_qs.count(), len(new_unit_list))
		for unit in unit_qs:
			self.assertEqual(unit.unit_class.name, "Archer")

		# Rerun command, but with a bad unit name, should not have new units
		bad_unit_list = []
		for _ in range(0, self.version.unit_min):
			bad_unit_list.append("Mage")
		bad_unit_list.append("fake_unit")
		self.st_cmd["Units"] = bad_unit_list

		self.helper_execute_failure(self.st_cmd, "The following are not valid unit selections: fake_unit")

		unit_qs = Unit.objects.filter(owner=self.user)

		self.assertEqual(unit_qs.count(), len(new_unit_list))
		for unit in unit_qs:
			self.assertEqual(unit.unit_class.name, "Archer")

class TestFindMatch(TestGame):
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

	def test_fm_03_already_in_queue(self):
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)
		self.helper_execute_failure(self.fm_cmd,
			"You are alrerady in the matchmaking queue for a game.")

		# Ensure the user is only in the queue once
		game_queue_count = Game_Queue.objects.filter(user=self.user).count()
		self.assertEqual(game_queue_count, 1)

	def test_fm_04_cancel_search_success(self):
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)

		self.assertTrue(Game_Queue.objects.count() == 1)

		# Test Cancel Game Search succeeds
		self.helper_execute_success(self.cs_cmd)
		self.assertTrue(Game_Queue.objects.count() == 0)

		# Test Cancel Game Search succeeds even when user isn't in the queue
		self.helper_execute_success(self.cs_cmd)

class TestMatchmaking(TestGame):
	"""
	All tests within this class relate specifically to the matchmaking logic.

	Specifically, the following is tested:\n
	- When two players are matched: (Test 01)\n
		+ They are each removed from the Game Queue\n
		+ They are each added as Game Users as a pair\n
		+ Their Game User name includes the other player's name and the game count between them\n
		+ A game object was created for them\n
		+ Each of their units was added to the game\n
	- When one player is in the queue, nothing happens (Test 02)\n
	- When two players are matched more than once, the counter increases properly (Test 03)\n
	"""
	def setUp(self):
		super(TestMatchmaking, self).setUp()

		self.get_both_users_in_queue()

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

	def test_mm_02_one_user_test(self):
		# Remove both users from the queue
		Game_Queue.objects.filter().delete()

		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)

		processMatchmakingQueue()

		# Ensure no game users were created
		self.assertTrue(Game_User.objects.exclude(game=None).count() == 0)

		# Ensure the user was not removed from queue
		self.assertTrue(Game_Queue.objects.count() == 1)

	def test_mm_03_two_games_matched(self):
		processMatchmakingQueue()

		# Get both players in the queue again and match again
		self.helper_execute_success(self.st_cmd)
		self.helper_execute_success(self.fm_cmd)
		self.helper_execute_success(self.st_cmd, 2)
		self.helper_execute_success(self.fm_cmd, 2)
		processMatchmakingQueue()

		# Ensure the Game_User objects were created properly
		self.assertTrue(len(Game_User.objects.filter(game=None)) == 0)
		self.assertEquals(Game_User.objects.filter(user=self.user, name="vs. game_user_2 #1").count(), 1)
		self.assertEquals(Game_User.objects.filter(user=self.user, name="vs. game_user_2 #1").first().team, 1)
		self.assertEquals(Game_User.objects.filter(user=self.user, name="vs. game_user_2 #2").count(), 1)
		self.assertEquals(Game_User.objects.filter(user=self.user, name="vs. game_user_2 #2").first().team, 1)
		self.assertEquals(Game_User.objects.filter(user=self.user2, name="vs. game_user_1 #1").count(), 1)
		self.assertEquals(Game_User.objects.filter(user=self.user2, name="vs. game_user_1 #1").first().team, 2)
		self.assertEquals(Game_User.objects.filter(user=self.user2, name="vs. game_user_1 #2").count(), 1)
		self.assertEquals(Game_User.objects.filter(user=self.user2, name="vs. game_user_1 #2").first().team, 2)

		# Ensure all of each player's units were assigned to the game
		self.assertEquals(len(Unit.objects.filter(owner=self.user, game=None)), 0)
		self.assertEquals(len(Unit.objects.filter(owner=self.user2, game=None)), 0)

		# Ensure that both games were created
		self.assertTrue(Game.objects.count() == 2)

		# Ensure that the Game Queue is now empty
		self.assertTrue(Game_Queue.objects.count() == 0)

class TestPlaceUnits(TestGame):
	"""
	All tests within this class relate specifically to the command 'PU' (Place Units)

	The following is tested:\n
	- The command missing either the Game or Units keys returns an error (Test 01)\n
	- If the incorrect number of units is provided, an error is returned (Test 01)\n
	- Sending a bad game or unit name returns an error (Test 01)\n
	- Sending a game that you are not currently in returns an error (Test 01)\n
	- A group of units that does not match your set team returns an error (Test 01)\n
	- For the 'Units' dictionaries: Name, X, and Y must always exist (Test 01)\n
	- Units can only be placed in valid locations, which excludes: (Test 01)\m
		+ A random point in the map not for placement\n
		+ An opponents placement location\n
	- Calling the command properly returns success (Test 02)\n
	- For a successful call, each unit is properly placed in the database: (Test 02)\n
		+ In the game properly\n
		+ X and Y location updated\n
		+ Health updated\n
		+ Able to act\n
	- Placing units before matched with an opponent returns an error (Test 03)\n
	"""
	def setUp(self):
		super(TestPlaceUnits, self).setUp()

		self.get_both_users_in_queue()
		processMatchmakingQueue()
		self.game = Game.objects.latest('pk')

	def test_pu_01_bad_json(self):
		# Missing Game
		no_game_cmd = copy.deepcopy(self.pu_cmd)
		no_game_cmd.pop("Game", None)
		self.helper_execute_failure(no_game_cmd, "Internal Error: Game key missing.")

		# Missing Units
		no_units_cmd = copy.deepcopy(self.pu_cmd)
		no_units_cmd.pop("Units", None)
		self.helper_execute_failure(no_units_cmd, "Internal Error: Unit key missing.")

		# Invalid list count
		empty_units_cmd = copy.deepcopy(self.pu_cmd)
		empty_units_cmd["Units"] = []
		self.helper_execute_failure(empty_units_cmd,
			"Incorrect number of units selected: (8) required, (0) chosen.")

		# Bad game name
		bad_game_cmd = copy.deepcopy(self.pu_cmd)
		bad_game_cmd["Game"] = "bad_game_name"
		self.helper_execute_failure(bad_game_cmd,
			"Invalid game name (bad_game_name) for user {0}.".format(self.credentials["username"]))

		# Invalid list of units - not the set team
		inval_unit_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in inval_unit_cmd["Units"]:
			unit_dict["Name"] = "Archer"
		self.helper_execute_failure(inval_unit_cmd,
			"Can only place units selected for this game.")

		# Invalid list of units - bad unit name
		fake_unit_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in fake_unit_cmd["Units"]:
			unit_dict["Name"] = "fake_unit"
		self.helper_execute_failure(fake_unit_cmd,
			"Can only place units selected for this game.")

		# Missing Unit name
		no_unit_name_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in no_unit_name_cmd["Units"]:
			unit_dict.pop("Name", None)
		self.helper_execute_failure(no_unit_name_cmd, "Internal Error: Name of unit missing.")

		# Missing X
		no_x_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in no_x_cmd["Units"]:
			unit_dict.pop("X", None)
		self.helper_execute_failure(no_x_cmd, "Internal Error: Missing X or Y.")

		# Missing Y
		no_y_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in no_y_cmd["Units"]:
			unit_dict.pop("Y", None)
		self.helper_execute_failure(no_y_cmd, "Internal Error: Missing X or Y.")

		# Invalid placement location - random mid-point in map
		inval_place_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in inval_place_cmd["Units"]:
			unit_dict["Y"] = 8
		self.helper_execute_failure(inval_place_cmd,
			"Location X:0 Y:8 is not a valid placement location for a unit for your team.")

		# Invalid placement location - opponent placement location
		inval_place_cmd = copy.deepcopy(self.pu_cmd)
		for unit_dict in inval_place_cmd["Units"]:
			unit_dict["Y"] = 15
		self.helper_execute_failure(inval_place_cmd,
			"Location X:0 Y:15 is not a valid placement location for a unit for your team.")

	def test_pu_02_success(self):
		self.helper_execute_success(self.pu_cmd)

		units = Unit.objects.filter(owner=self.user, game=self.game)
		for unit in units:
			self.assertNotEqual(unit.x, -1)
			self.assertNotEqual(unit.y, -1)
			self.assertNotEqual(unit.hp, 0)
			self.assertFalse(unit.acted)

	def test_pu_03_not_matched(self):
		# Set team again to 0 to emulate placing units without a team side
		game_user_1 = Game_User.objects.filter(user=self.user).first()
		game_user_1.team = 0
		game_user_1.save()

		self.helper_execute_failure(self.pu_cmd,
			"You cannot place units until both players have set their teams.")

class TestQueryGames(TestGame):
	"""
	All tests within this class relate specifically to the command 'QGU' (Query Games for User)

	Specifically the following is tested:\n
	- Calling the command with one game with a single opponent returns successfully: (Test 01)\n
		+ One game dictionary is returned with the proper game name\n
	- Calling QGU when a set team that is not a matched game does not return an extra game (Test 02)\n
	"""
	def test_qgu_01_one_game_one_opponent(self):
		self.get_both_users_in_queue()
		processMatchmakingQueue()
		self.game = Game.objects.latest('pk')

		qgu_cmd = {"Command":"QGU"}

		result = self.helper_execute_success(qgu_cmd)

		self.assertTrue(len(result["Games"]) == 1)
		self.assertEquals(result["Games"][0]["Name"], Game_User.objects.filter(user=self.user).first().name)
		self.assertEquals(result["Games"][0]["Round"], Game.objects.filter().first().game_round)

	def test_qgu_02_set_team_not_matched(self):
		self.get_both_users_in_queue()
		processMatchmakingQueue()
		self.game = Game.objects.latest('pk')

		# Also set team for player 1 but don't pair with an opponent
		self.helper_execute_success(self.st_cmd)

		qgu_cmd = {"Command":"QGU"}

		result = self.helper_execute_success(qgu_cmd)

		self.assertTrue(len(result["Games"]) == 1)
		self.assertEquals(result["Games"][0]["Name"], Game_User.objects.filter(user=self.user).first().name)
		self.assertEquals(result["Games"][0]["Round"], Game.objects.filter().first().game_round)

class TestTakeAction(TestGame):
	"""
	All tests within this class relate specifically to the command 'TA' (Take Action)

	Specifically the following is tested:\n
	- Any of the following keys missing is caught: (Test 01)\n
		Game, Action, Unit, Target\n
	- A fake or invalid game name returns an error message (Test 01)\n
	- A fake or invalid action for the unit returns an error message (Test 01)\n
	- Either the new X or Y coordinate is missing (Test 01)\n
	- An invalid unit ID or target ID returns an error message (Test 01)\n
	- When attempting to move: (Test 02)\n
		+ Cannot move onto an ally unit\n
		+ Cannot move onto an enemy unit\n
		+ Cannot move through an enemy unit\n
		+ Is properly impeded by the terrain\n
	- Can successfully execute the 'Wait' action on own coordinates (Test 03)\n
	- Cannot act again after a successful action (Test 03)\n
	- Can successfully move only a partial amount of full movement range (Test 04)\n
	- Can move the full distance of unit's movement range successfully (Test 05)\n
	- Can move through an allied unit to get to target location (Test 06)\n
	- Cannot act before the opponent has placed their units (Test 07)\n
	- Cannot act before placing your own units (Test 08)\n
	- Can attack an enemy unit within range for normal damage, and: (Test 09)\n
		+ Handle the enemy target countering\n
		+ Both unit and target HPs are updated\n
		+ The returned JSON includes their current and new HPs\n
		+ Both IDs are returned to help reference them\n
	- Cannot heal self (Test 10)\n
	- Cannot heal an ally that has full HP, is dead, or out of range (Test 10)\n
	- Cannot heal an enenmy (Test 10)\n
	- Cannot attack self or an ally (Test 11)\n
	- Cannot attack an enemy that is dead or too far away (Test 11)\n
	- The attacker can land a critical hit for double damage (Test 12)\n
	- A dead target cannot counter attack (Test 12)\n
	- A ranged unit can successfully attack from range (Test 13)\n
	- A melee unit cannot counter attack a ranged unit from range (Test 13)\n
	- Attacking without moving executes successfully (Test 13)\n
	- The attacker can successfully miss (Test 14)\n
	- The counter attack can successfully get a critical hit (Test 14)\n
	- A unit that cannot attack will not counter attack (Test 15)\n
	- A target can successfully miss their counter attack (Test 16)\n
	- A healer can successfully heal (Test 17)\n
	- Healing will not bring the target above full health (Test 17)\n
	- Can heal the partial, but not full HP, if HP is low (Test 18)\n
	- Can heal exactly to full HP (Test 19)\n
	- Cannot take an action if it is not your turn (Test 20)\n
	- Both a magical and physical attacker can successfully deal damage (Test 21)\n
	"""
	def setUp(self):
		super(TestTakeAction, self).setUp()

		# Get both users into a game
		self.get_both_users_in_queue()
		processMatchmakingQueue()
		self.game = Game.objects.latest('pk')

		# Place units for player one
		self.helper_execute_success(self.pu_cmd)

		# Place units for player two
		self.pu_cmd2 = {
			"Command" : "PU",
			"Game"    : "vs. {0} #1".format(self.credentials["username"]),
			"Units"   : self.place_valid_team_dict(self.st_cmd["Units"], 2)
		}
		self.helper_execute_success(self.pu_cmd2, 2)

		# Print a table of the placed units
		for unit in Unit.objects.filter(game=self.game):
			logging.debug("Unit: X: %d\t Y: %d\t ID: %d\t Name: %s\t Owner: %s", unit.x, unit.y,
				unit.pk, unit.unit_class.name, unit.owner.username)
			
		# Ensure it is player one's turn
		self.game.user_turn = self.user
		self.game.save()

		# Ensure on map 'Grassland'
		map_obj = Map.objects.filter(version=self.version, name="Grassland").first()
		self.game.map_path = map_obj
		self.game.save()

		# Commonly used units
		self.heal_class = Class.objects.filter(name="Cleric", version=self.version).first()
		self.attacker  = Unit.objects.filter(game=self.game, owner=self.user).exclude(
			unit_class=self.heal_class).first()
		self.healer  = Unit.objects.filter(game=self.game, owner=self.user,
			unit_class=self.heal_class).first()
		self.enemy_tgt = Unit.objects.filter(game=self.game, owner=self.user2).exclude(
			unit_class=self.attacker.unit_class).exclude(unit_class=self.healer.unit_class).first()

		# Find a reliable, nearby ally
		self.nearest_ally_x = self.attacker.x - 1 if self.attacker.x != 0 else self.attacker.x + 1
		self.nearest_ally = Unit.objects.filter(owner=self.user, game=self.game,
			x=self.nearest_ally_x).first()

		# Find the attacking unit's movement range
		move = Stat.objects.filter(name="Move", version=self.version).first()
		self.attacker_mv_rng = Unit_Stat.objects.filter(unit=self.attacker.unit_class,
			stat=move, version=self.version).first().value

		# Take Action - No target
		self.no_tgt_cmd = {
			"Command" : "TA",
			"Action"  : "Wait",
			"Game"    : "vs. {0} #1".format(self.credentials2["username"]),
			"Unit"    : self.attacker.id,
			"X"       : 1,
			"Y"       : 1
		}

		# Take Action - Attack
		self.atk_cmd = copy.deepcopy(self.no_tgt_cmd)
		self.atk_cmd["Action"] = "Attack"
		self.atk_cmd["Target"] = self.enemy_tgt.id

		# Take Action - Heal
		self.heal_cmd = copy.deepcopy(self.no_tgt_cmd)
		self.heal_cmd["Action"] = "Heal"
		self.heal_cmd["Unit"]   = self.healer.id
		self.heal_cmd["Target"] = self.nearest_ally.id

	def helper_execute_move_success(self, command):
		"""
		Helper class used to verify a successful movement
		Issues the provided (Take action) command and then verifies
		that the unit actually moved to the new location in the DB
		The result of the action is then returned to allow for 
		verifying other parts of the test
		"""		
		newX = command["X"]
		newY = command["Y"]

		result = self.helper_execute_success(command)

		moved_unit = Unit.objects.filter(pk=command["Unit"]).first()

		# Ensure the new location was saved in the database
		self.assertEqual(moved_unit.x, newX)
		self.assertEqual(moved_unit.y, newY)

		# Ensure the new location is in the JSON response
		self.assertEqual(result["Unit"]["NewX"], newX)
		self.assertEqual(result["Unit"]["NewY"], newY)
		self.assertEqual(result["Unit"]["ID"], moved_unit.id)

		return result

	def helper_execute_attack_success(self, command):
		"""
		Helper class which issues the provided (attack) command and then verifies
		each unit's max HP and IDs in the JSON.

		Also computes the expected result if either attack was a crit, miss, or normal attack

		All of this, as well as the updates units are returned as a list
		"""
		result = self.helper_execute_move_success(command)

		# Ensure the target's ID is in the JSON properly
		self.assertEqual(result["Target"]["ID"], command["Target"])

		# Get updated units
		unit = Unit.objects.filter(pk=command["Unit"]).first()
		tgt = Unit.objects.filter(pk=command["Target"]).first()

		# Get all possible attack results
		attack_data = self.get_expected_attack_result(unit.unit_class, tgt.unit_class)

		# Ensure that the previous health for each unit is correct - left at max
		self.assertEqual(result["Unit"]["HP"], attack_data["Unit"]["Max"])
		self.assertEqual(result["Target"]["HP"], attack_data["Tgt"]["Max"])

		return [result, unit, tgt, attack_data]

	def helper_execute_heal_success(self, command):
		"""
		Helper class which issues the provided (heal) command and then verifies
		each unit's ID in the JSON.  For heals the HP will not normally be at max
		before the action takes place.

		Also computes the expected result if either attack was a crit, miss, or normal attack

		All of this, as well as the updates units are returned as a list
		"""
		result = self.helper_execute_move_success(command)

		# Ensure the target's ID is in the JSON properly
		self.assertEqual(result["Target"]["ID"], command["Target"])

		# Get updated units
		unit = Unit.objects.filter(pk=command["Unit"]).first()
		tgt = Unit.objects.filter(pk=command["Target"]).first()

		# Heals act the same as attacks, just only "normal" as an option
		heal_data = self.get_expected_attack_result(unit.unit_class, tgt.unit_class)

		# Healer's HP should remain constant at max HP
		self.assertEqual(unit.hp, heal_data["Unit"]["Max"])
		self.assertEqual(result["Unit"]["HP"], heal_data["Unit"]["Max"])
		self.assertEqual(result["Unit"]["NewHP"], heal_data["Unit"]["Max"])

		return [result, unit, tgt, heal_data]

	def get_expected_attack_result(self, unit, tgt):
		"""
		Determine the expected result of the two units attacking each other
		Create a dictionary of all three possible health values for each unit,
		being if the other unit got a crit, miss, or normal hit

		unit should be the CLASS of the attacking unit
		tgt should be the CLASS of the target unit

		:rtype: Dictionary
		:return: The following object:\n
			{\n
				"Unit":{\n
					"Max":12,\n
					"Normal":10,\n
					"Crit":6,\n
					"Miss":12,\n
				}n
				"Tgt":{\n
					"Max":12,\n
					"Normal":8,\n
					"Crit":4,\n
					"Miss":12,\n
				}n
			}
		"""
		hp    = Stat.objects.filter(name="HP",           version=self.version).first()
		strn  = Stat.objects.filter(name="Strength",     version=self.version).first()
		intel = Stat.objects.filter(name="Intelligence", version=self.version).first()
		defn  = Stat.objects.filter(name="Defense",      version=self.version).first()
		res   = Stat.objects.filter(name="Resistance",   version=self.version).first()

		# Unit values
		u_hp  = Unit_Stat.objects.filter(unit=unit, stat=hp,    version=self.version).first().value
		u_str = Unit_Stat.objects.filter(unit=unit, stat=strn,  version=self.version).first().value
		u_int = Unit_Stat.objects.filter(unit=unit, stat=intel, version=self.version).first().value
		u_def = Unit_Stat.objects.filter(unit=unit, stat=defn,  version=self.version).first().value
		u_res = Unit_Stat.objects.filter(unit=unit, stat=res,   version=self.version).first().value
		u_atk_type = unit.attack_type

		# Target values
		t_hp  = Unit_Stat.objects.filter(unit=tgt, stat=hp,    version=self.version).first().value
		t_str = Unit_Stat.objects.filter(unit=tgt, stat=strn,  version=self.version).first().value
		t_int = Unit_Stat.objects.filter(unit=tgt, stat=intel, version=self.version).first().value
		t_def = Unit_Stat.objects.filter(unit=tgt, stat=defn,  version=self.version).first().value
		t_res = Unit_Stat.objects.filter(unit=tgt, stat=res,   version=self.version).first().value
		t_atk_type = tgt.attack_type

		data = {}

		# Possible HP remaining values for Unit
		data["Unit"] = {}
		data["Unit"]["Max"] = u_hp
		data["Unit"]["Normal"] = max(0, u_hp - max(0, math.ceil((t_str - u_def) / 2)) if t_atk_type == "Physical"
			else math.ceil((t_int - u_res) / 2))
		data["Unit"]["Crit"] = max(0, u_hp - max(0, math.ceil(((2 * t_str) - u_def) / 2)) if t_atk_type == "Physical"
			else math.ceil(((2 * t_int) - u_res) / 2))
		data["Unit"]["Miss"] = u_hp

		# Possible HP remaining values for Target
		data["Tgt"] = {}
		data["Tgt"]["Max"] = t_hp
		data["Tgt"]["Normal"] = max(0, t_hp - max(0, u_str - t_def if u_atk_type == "Physical"
			else u_int - t_res))
		data["Tgt"]["Crit"] = max(0, t_hp - max(0, (2 * u_str) - t_def if u_atk_type == "Physical"
			else (2 * u_int) - t_res))
		data["Tgt"]["Miss"] = t_hp

		# The amount that SHOULD have been healed - not new HP
		data["Tgt"]["Heal"] = u_str - t_def if u_atk_type == "Physical" else u_int - t_res

		return data

	def set_luck_and_agil(self,unit_class, luck_val, agil_val):
		"""
		Takes in the class object of a unit whose luck and agility values are to be
		updated to the values provided
		"""
		Static.statichelper.static_data = {}

		luck = Stat.objects.filter(name="Luck", version=self.version).first()
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=unit_class,
			version=self.version).first()
		unit_luck.value = luck_val
		unit_luck.save()

		agil = Stat.objects.filter(name="Agility", version=self.version).first()
		unit_agil = Unit_Stat.objects.filter(stat=agil, unit=unit_class,
			version=self.version).first()
		unit_agil.value = agil_val
		unit_agil.save()

	def move_unit_near_target(self, cmd, unit, target, distance=2):
		"""
		Will move the unit specified in the DB just north of the target unit.
		It will be 'distance' spaces away and will end one space closer than that.
		The default is to have the unit two spaces away and have it move within melee range.
		"""
		unit.x = target.x
		unit.y = target.y - distance
		unit.save()

		# Move south one unit
		cmd["X"] = unit.x
		cmd["Y"] = target.y - (distance - 1)

		return cmd

	def test_ta_01_bad_json(self):
		# A missing game key
		no_game_command = copy.deepcopy(self.no_tgt_cmd)
		no_game_command.pop("Game", None)
		self.helper_execute_failure(no_game_command, "Internal Error: Game Key missing.")

		# A fake game name
		fake_game_command = copy.deepcopy(self.no_tgt_cmd)
		fake_game_command["Game"] = "fake_game_name"
		self.helper_execute_failure(fake_game_command, "No match for game of name fake_game_name.")
		
		# Existing, but bad name
		inval_game_command = copy.deepcopy(self.no_tgt_cmd)
		inval_game_command["Game"] = "vs. {0} #1".format(self.credentials["username"])
		self.helper_execute_failure(inval_game_command,
			"No match for game of name vs. {0} #1.".format(self.credentials["username"]))

		# Test action key missing
		no_action_command = copy.deepcopy(self.no_tgt_cmd)
		no_action_command.pop("Action", None)
		self.helper_execute_failure(no_action_command, "Internal Error: Action Key missing.")

		# Test an invalid action key value
		fake_action_command = copy.deepcopy(self.no_tgt_cmd)
		fake_action_command["Action"] = "fake_action"
		self.helper_execute_failure(fake_action_command, "The selected action is not valid.")

		# Test an invalid action for the specific unit - attacker cannot heal
		bad_action_command = copy.deepcopy(self.atk_cmd)
		bad_action_command["Action"] = "Heal"
		self.helper_execute_failure(bad_action_command, "The selected action is not valid.")

		# Location information missing - No X
		missing_x_command = copy.deepcopy(self.no_tgt_cmd)
		missing_x_command.pop("X", None)
		self.helper_execute_failure(missing_x_command,
			"Internal Error: New location information incomplete.")

		# Location information missing - No Y
		missing_y_command = copy.deepcopy(self.no_tgt_cmd)
		missing_y_command.pop("Y", None)
		self.helper_execute_failure(missing_y_command,
			"Internal Error: New location information incomplete.")

		# Unit key missing
		no_unit_command = copy.deepcopy(self.no_tgt_cmd)
		no_unit_command.pop("Unit", None)
		self.helper_execute_failure(no_unit_command, "Internal Error: Unit Key missing.")

		# Test an invalid unit key value
		bad_unit_command = copy.deepcopy(self.no_tgt_cmd)
		bad_unit_command["Unit"] = -1
		self.helper_execute_failure(bad_unit_command,
			"Internal Error: Specified unit ID not in game.")

		# Test target key missing
		missing_target_command = copy.deepcopy(self.atk_cmd)
		missing_target_command.pop("Target", None)
		self.helper_execute_failure(missing_target_command, "Internal Error: Target Key missing.")

		# Test target key invalid unit
		bad_target_command = copy.deepcopy(self.atk_cmd)
		bad_target_command["Target"] = -1
		self.helper_execute_failure(bad_target_command,
			"Internal Error: Specified target ID not in game.")

	def test_ta_02_bad_move(self):
		# Moving onto ally unit
		ally_move_command = copy.deepcopy(self.no_tgt_cmd)
		ally_move_command["X"] = self.nearest_ally_x
		ally_move_command["Y"] = 0
		self.helper_execute_failure(ally_move_command,
			"Location ({0},0) occupied by an ally. Can move through, but not to, that token.".format(
				self.nearest_ally_x))

		# Move near enemy for next tests
		self.attacker.x = self.enemy_tgt.x
		self.attacker.y = self.enemy_tgt.y - 1
		self.attacker.save()

		# Moving onto enemy unit
		enemy_move_command = copy.deepcopy(self.no_tgt_cmd)
		enemy_move_command["X"] = self.enemy_tgt.x
		enemy_move_command["Y"] = self.enemy_tgt.y
		self.helper_execute_failure(enemy_move_command,
			"Location ({0},{1}) occupied by an enemy. Cannot move to that token.".format(
				self.enemy_tgt.x, self.enemy_tgt.y))

		# Move enemy directly above attacker
		self.enemy_tgt.y -= 2
		self.enemy_tgt.save()

		# Try moving through enemy unit
		move_through_enemy_command = copy.deepcopy(self.no_tgt_cmd)
		move_through_enemy_command["X"] = self.enemy_tgt.x
		move_through_enemy_command["Y"] = self.attacker.y - self.attacker_mv_rng
		self.helper_execute_failure(move_through_enemy_command,
			"Target location ({0},{1}) was out of reach for {2} at location ({3},{4}).".format(
				self.enemy_tgt.x, (self.attacker.y - self.attacker_mv_rng),
				self.attacker.unit_class.name,
				self.attacker.x, self.attacker.y))

		# Ensure on map with forest
		map_obj = Map.objects.filter(version=self.version, name="Forest Pattern").first()
		self.game.map_path = map_obj
		self.game.save()

		# Move the attacker to a place to test forest movement
		forest_row = 7
		self.attacker.x = 0
		self.attacker.y = forest_row
		self.attacker.save()

		# Forest impedes full movement
		move_through_forest_command = copy.deepcopy(self.no_tgt_cmd)
		move_through_forest_command["X"] = self.attacker.x + self.attacker_mv_rng
		move_through_forest_command["Y"] = forest_row
		self.helper_execute_failure(move_through_forest_command,
			"Target location ({0},{1}) was out of reach for {2} at location ({3},{4}).".format(
				(self.attacker.x + self.attacker_mv_rng), forest_row,
				self.attacker.unit_class.name,
				self.attacker.x, self.attacker.y))

	def test_ta_03_move_on_self_success(self):
		# Set target coordinates to self
		self.no_tgt_cmd["X"] = self.attacker.x
		self.no_tgt_cmd["Y"] = self.attacker.y

		self.helper_execute_move_success(self.no_tgt_cmd)

		# Ensure the same unit cannot act again this turn
		self.helper_execute_failure(self.no_tgt_cmd, "That unit has already acted this turn.")

	def test_ta_04_partial_move_success(self):
		# Move one distance south
		self.no_tgt_cmd["X"] = self.attacker.x
		self.no_tgt_cmd["Y"] = self.attacker.y + 1

		self.helper_execute_move_success(self.no_tgt_cmd)

	def test_ta_05_full_move_success(self):
		# Move full distance south
		self.no_tgt_cmd["X"] = self.attacker.x
		self.no_tgt_cmd["Y"] = self.attacker.y + self.attacker_mv_rng

		self.helper_execute_move_success(self.no_tgt_cmd)

	def test_ta_06_move_through_ally_success(self):
		# Move unit to location (0,1)
		self.attacker.x = 0
		self.attacker.y = 1
		self.attacker.save()

		# Move ally to location (1,1) - to have to move through
		self.healer.x = 1
		self.healer.y = 1
		self.healer.save()

		# Moving full distance east through ally unit
		self.no_tgt_cmd["X"] = self.attacker.x + self.attacker_mv_rng
		self.no_tgt_cmd["Y"] = self.attacker.y

		self.helper_execute_move_success(self.no_tgt_cmd)

	def test_ta_07_before_enemy_placement(self):
		# Undo the placing of the opponent's units
		Unit.objects.filter(owner=self.user2).update(x=-1, y=-1)

		# Call take action before the opponent has placed their units
		self.helper_execute_failure(self.no_tgt_cmd,
			"Please wait until your opponent places their units before taking a turn.")

	def test_ta_08_before_own_placement(self):
		# Undo the placing of user's units
		Unit.objects.filter(owner=self.user).update(x=-1, y=-1)

		# Call take action before placing units
		self.helper_execute_failure(self.no_tgt_cmd,
			"You must place all of your units before taking a turn.")

	def test_ta_09_basic_attack_success(self):
		# Ensure the attacker cannot crit (But maybe enemy can) and always hits
		self.set_luck_and_agil(self.attacker.unit_class, -5, 15)

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, self.enemy_tgt)

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Verify target's new HP
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Normal"])

		# Verify unit's HP after target's counter attack
		self.assertTrue(
			unit.hp == attack_data["Unit"]["Normal"] or 
			unit.hp == attack_data["Unit"]["Crit"] or 
			unit.hp == attack_data["Unit"]["Miss"],
			msg="unit.hp={0}, attack_data={1}".format(unit.hp, attack_data["Unit"])
		)

		# Verify returned JSON
		self.assertTrue(result["Unit"]["NewHP"] == attack_data["Unit"]["Normal"] or 
						result["Unit"]["NewHP"] == attack_data["Unit"]["Crit"] or 
						result["Unit"]["NewHP"] == attack_data["Unit"]["Miss"],
						msg="unit.hp={0}, attack_data={1}".format(unit.hp, attack_data["Unit"]))
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Normal"])

	def test_ta_10_bad_heal(self):
		nearest_ally = Unit.objects.filter(owner=self.user, 
			x=self.healer.x - 1 if self.healer.x != 0 else 1).first()

		# Trying to heal self
		heal_self_command = copy.deepcopy(self.heal_cmd)
		heal_self_command["Target"] = self.healer.id
		self.helper_execute_failure(heal_self_command, "Cannot target self.")

		# Trying to heal ally at full health
		heal_full_hp_command = copy.deepcopy(self.heal_cmd)
		heal_full_hp_command["X"] = self.healer.x
		heal_full_hp_command["Y"] = self.healer.y
		heal_full_hp_command["Target"] = nearest_ally.id
		self.helper_execute_failure(heal_full_hp_command, "Target already has full Health.")

		# Trying to heal ally that is dead
		nearest_ally.hp = 0 			# He died :(
		nearest_ally.save()
		heal_dead_command = copy.deepcopy(self.heal_cmd)
		heal_dead_command["X"] = self.healer.x
		heal_dead_command["Y"] = self.healer.y
		heal_dead_command["Target"] = nearest_ally.id
		self.helper_execute_failure(heal_dead_command, "You cannot heal dead units.")

		# Trying to heal target too far away
		distance = 4
		nearest_ally.hp = 3 			# He not died :)
		nearest_ally.x = self.healer.x
		nearest_ally.y = self.healer.y + distance
		nearest_ally.save()
		heal_far_command = copy.deepcopy(self.heal_cmd)
		heal_far_command["X"] = self.healer.x
		heal_far_command["Y"] = self.healer.y
		heal_far_command["Target"] = nearest_ally.id
		self.helper_execute_failure(heal_dead_command, 
			"Must be within 2 range.  Target is {0} away.".format(distance))

		# Trying to heal the enemy
		self.healer.x = self.enemy_tgt.x
		self.healer.y = self.enemy_tgt.y - 2
		self.healer.save()
		heal_far_command = copy.deepcopy(self.heal_cmd)
		heal_far_command["X"] = self.healer.x
		heal_far_command["Y"] = self.healer.y + 1
		heal_far_command["Target"] = self.enemy_tgt.id
		self.helper_execute_failure(heal_far_command, "Cannot heal the enemy units!")

	def test_ta_11_bad_attack(self):
		nearest_ally = Unit.objects.filter(owner=self.user, 
			x=self.attacker.x - 1 if self.attacker.x != 0 else 1).first()

		# Trying to attack self
		atk_self_command = copy.deepcopy(self.atk_cmd)
		atk_self_command["Target"] = self.attacker.id
		self.helper_execute_failure(atk_self_command, "Cannot target self.")

		# Trying to attack an ally
		atk_ally_command = copy.deepcopy(self.atk_cmd)
		atk_ally_command["X"] = self.attacker.x
		atk_ally_command["Y"] = self.attacker.y
		atk_ally_command["Target"] = nearest_ally.id
		self.helper_execute_failure(atk_ally_command, "Cannot attack your own units!")

		# Move a little closer to the enemy
		distance = 3
		self.attacker.x = self.enemy_tgt.x
		self.attacker.y = self.enemy_tgt.y - distance
		self.attacker.save()

		# Trying to attack target too far away
		atk_far_command = copy.deepcopy(self.atk_cmd)
		atk_far_command["X"] = self.attacker.x
		atk_far_command["Y"] = self.attacker.y
		self.helper_execute_failure(atk_far_command,
			"Must be within 2 range.  Target is {0} away.".format(distance))

		# Trying to attack an enemy that is dead
		self.enemy_tgt.hp = 0
		self.enemy_tgt.save()
		atk_dead_command = copy.deepcopy(self.atk_cmd)
		atk_dead_command["X"] = self.attacker.x
		atk_dead_command["Y"] = self.enemy_tgt.y - 1
		self.helper_execute_failure(atk_dead_command, "You cannot attack dead units.")

	def test_ta_12_crit_attack_success(self):
		# Ensure the attacker always crits and always hits
		self.set_luck_and_agil(self.attacker.unit_class, 100, 15)

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, self.enemy_tgt)

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Ensure database was updated properly
		self.assertEqual(unit.hp, attack_data["Unit"]["Max"])
		self.assertEqual(tgt.hp, 0)

		# Ensure returned JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], attack_data["Unit"]["Max"])
		self.assertEqual(result["Target"]["NewHP"], 0)

	def test_ta_13_attack_no_counter_success(self):
		atk_rng = Stat.objects.filter(name="Attack Range", version=self.version).first()
		
		# Get a ranged unit as the attacker
		ranged_objs = Unit_Stat.objects.filter(stat=atk_rng, value=2, version=self.version)
		for rngd_obj in ranged_objs:
			if rngd_obj.unit != self.heal_class:
				attacker_clss = rngd_obj.unit
				break
		attacker = Unit.objects.filter(owner=self.user, unit_class=attacker_clss,
			game=self.game).first()
		self.atk_cmd["Unit"] = attacker.id

		# Get a melee unit as the enemy target
		melee_obj = Unit_Stat.objects.filter(stat=atk_rng, value=1,
			version=self.version).first()
		target_clss = melee_obj.unit
		enemy = Unit.objects.filter(owner=self.user2, unit_class=target_clss,
			game=self.game).first()
		self.atk_cmd["Target"] = enemy.id

		# Ensure the attacker cannot crit and always hits
		self.set_luck_and_agil(attacker.unit_class, -5, 15)

		# Move unit near target
		attacker.x = enemy.x
		attacker.y = enemy.y - 2
		attacker.save()

		# Not moving at all - remain out of melee range
		self.atk_cmd["X"] = attacker.x
		self.atk_cmd["Y"] = attacker.y

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Ensure database updates are correct
		self.assertEqual(unit.hp, attack_data["Unit"]["Max"])
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Normal"])

		# Ensure JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], attack_data["Unit"]["Max"])
		self.assertEqual(result["Target"]["ID"], tgt.id)
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Normal"])

	def test_ta_14_attack_miss_success(self):
		# Ensure the attacker will miss and the counter will be a crit
		self.set_luck_and_agil(self.attacker.unit_class, -100, -100)

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, self.enemy_tgt)

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Ensure database was updated properly
		self.assertEqual(unit.hp, attack_data["Unit"]["Crit"])
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Miss"])

		# Ensure JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], attack_data["Unit"]["Crit"])
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Miss"])

	def test_ta_15_tgt_passive_success(self):
		# Get a target that cannot attack (healer)
		enemy_target = Unit.objects.filter(owner=self.user2, unit_class=self.heal_class,
			game=self.game).first()
		self.atk_cmd["Target"] = enemy_target.id

		# Ensure the attacker will miss - don't want to kill the lowly healer
		self.set_luck_and_agil(self.attacker.unit_class, -100, -100)

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, enemy_target)

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Ensure that the DB was updated properly
		self.assertEqual(unit.hp, attack_data["Unit"]["Max"])
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Max"])

		# Ensure that the JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], attack_data["Unit"]["Max"])
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Max"])

	def test_ta_16_counter_misses_success(self):
		# Ensure the attacker will hit and the counter will miss (no crit too)
		self.set_luck_and_agil(self.attacker.unit_class, -100, 100)

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, self.enemy_tgt)

		# Call command, ensure movement was successful
		result, unit, tgt, attack_data = self.helper_execute_attack_success(self.atk_cmd)

		# Ensure the DB was updated properly
		self.assertEqual(unit.hp, attack_data["Unit"]["Miss"])
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Normal"])

		# Ensure that the JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], attack_data["Unit"]["Miss"])
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Normal"])

	def test_ta_17_heal_fully_success(self):
		# Simulate target losing 1 health
		hp_lost = 1
		self.nearest_ally.hp -= hp_lost
		self.nearest_ally.save()

		# Move onto self
		self.heal_cmd["X"] = self.healer.x
		self.heal_cmd["Y"] = self.healer.y

		# Execute the command
		result, unit, tgt, heal_data = self.helper_execute_heal_success(self.heal_cmd)

		# Ensure the DB was updated properly
		self.assertEqual(tgt.hp, heal_data["Tgt"]["Max"])

		# Make sure the JSON is correct
		self.assertEqual(result["Target"]["HP"], heal_data["Tgt"]["Max"] - hp_lost)
		self.assertEqual(result["Target"]["NewHP"], heal_data["Tgt"]["Max"])

	def test_ta_18_heal_partial_success(self):
		# Simulate target losing all but 1 health
		self.nearest_ally.hp = 1
		self.nearest_ally.save()

		# Move onto self
		self.heal_cmd["X"] = self.healer.x
		self.heal_cmd["Y"] = self.healer.y

		# Execute the command
		result, unit, tgt, heal_data = self.helper_execute_heal_success(self.heal_cmd)

		# Ensure the DB was updated properly
		self.assertEqual(tgt.hp, 1 + heal_data["Tgt"]["Heal"])
		self.assertTrue(tgt.hp < heal_data["Tgt"]["Max"])

		# Make sure JSON is correct
		self.assertEqual(result["Target"]["HP"], 1)
		self.assertEqual(result["Target"]["NewHP"], 1 + heal_data["Tgt"]["Heal"])
		self.assertTrue(result["Target"]["NewHP"] < heal_data["Tgt"]["Max"])

	def test_ta_19_heal_exact_full_success(self):
		# Determine how much HP would be healed
		heal_data = self.get_expected_attack_result(self.healer.unit_class,
			self.nearest_ally.unit_class)

		# Simulate target losing the amount to be exactly, fully healed
		self.nearest_ally.hp -= heal_data["Tgt"]["Heal"]
		self.nearest_ally.save()

		# Move onto self
		self.heal_cmd["X"] = self.healer.x
		self.heal_cmd["Y"] = self.healer.y

		# Execute the command
		result, unit, tgt, heal_data = self.helper_execute_heal_success(self.heal_cmd)

		# Ensure the DB was updated properly
		self.assertEqual(tgt.hp, heal_data["Tgt"]["Max"])

		# Make sure JSON is correct
		self.assertEqual(result["Target"]["HP"], heal_data["Tgt"]["Max"] - heal_data["Tgt"]["Heal"])
		self.assertEqual(result["Target"]["NewHP"], heal_data["Tgt"]["Max"])

	def test_ta_20_act_on_enemy_turn(self):
		# Ensure it is player two's turn
		self.game.user_turn = self.user2
		self.game.save()

		self.helper_execute_failure(self.no_tgt_cmd, "Please wait until it is your turn.")

	def test_ta_21_magical_counterattack(self):
		# Ensure the attacker never hits or crits
		self.set_luck_and_agil(self.attacker.unit_class, -100, -100)

		# Make the attacker near death
		self.attacker.hp = 1
		self.attacker.save()

		# Make the target the magical 'Mage'
		mage_class = Class.objects.filter(name="Mage", version=self.version).first()
		mage_unit  = Unit.objects.filter(unit_class=mage_class, owner=self.user2).first()
		self.atk_cmd["Target"] = mage_unit.id

		# Move unit near target
		self.atk_cmd = self.move_unit_near_target(self.atk_cmd, self.attacker, mage_unit)

		# Call command, ensure movement was successful
		result = self.helper_execute_success(self.atk_cmd)

		# Get updated units
		unit = Unit.objects.filter(pk=self.atk_cmd["Unit"]).first()
		tgt = Unit.objects.filter(pk=self.atk_cmd["Target"]).first()

		# Get all possible attack results
		attack_data = self.get_expected_attack_result(unit.unit_class, tgt.unit_class)

		# Ensure that the previous health for each unit is correct
		self.assertEqual(result["Unit"]["HP"], 1)
		self.assertEqual(result["Target"]["HP"], attack_data["Tgt"]["Max"])

		# Ensure database was updated properly
		self.assertEqual(unit.hp, 0)
		self.assertEqual(tgt.hp, attack_data["Tgt"]["Max"])

		# Ensure returned JSON is correct
		self.assertEqual(result["Unit"]["NewHP"], 0)
		self.assertEqual(result["Target"]["NewHP"], attack_data["Tgt"]["Max"])

class TestEndTurn(TestGame):
	"""
	Handles all tests related specifically to the command "ET" (End Turn)

	Specifically tests that:\n
	- Game key missing returns an error message (Test 01)\n
	- Fake or invalid game names return an error message (Test 01)\n
	- Cannot end turn when it is not your turn (Test 02)\n
	- Ending turn can be called successfully when it is your turn, and: (Test 03)\n
		+ The turn value in the game is toggled to the other player\n
		+ Each of the other player's units can now act
	"""
	def setUp(self):
		super(TestEndTurn, self).setUp()

		# Get both users into a game
		self.get_both_users_in_queue()
		processMatchmakingQueue()
		self.game = Game.objects.latest('pk')

		# Place units for player one
		self.helper_execute_success(self.pu_cmd)

		# Place units for player two
		self.pu_cmd2 = {
			"Command" : "PU",
			"Game"    : "vs. {0} #1".format(self.credentials["username"]),
			"Units"   : self.place_valid_team_dict(self.st_cmd["Units"], 2)
		}
		self.helper_execute_success(self.pu_cmd2, 2)

		# Ensure it is player one's turn
		self.game.user_turn = self.user
		self.game.save()

		# The end turn command, with valid JSON
		self.et_cmd = {
			"Command" : "ET",
			"Game"    : "vs. {0} #1".format(self.credentials2["username"])
		}

	def test_et_01_bad_json(self):
		# Test a missing game key
		no_game_cmd = copy.deepcopy(self.et_cmd)
		no_game_cmd.pop("Game", None)
		self.helper_execute_failure(no_game_cmd, "Internal Error: Game Key missing.")

		# Test an invalid game key value - fake name
		fake_game_cmd = copy.deepcopy(self.et_cmd)
		fake_game_cmd["Game"] = "fake_game_name"
		self.helper_execute_failure(fake_game_cmd, "No match for game of name fake_game_name.")

		# Test an existing, but bad, game name
		bad_game_cmd = copy.deepcopy(self.et_cmd)
		bad_game_cmd["Game"] = "vs. {0} #1".format(self.credentials["username"])
		self.helper_execute_failure(bad_game_cmd, "No match for game of name vs. {0} #1.".format(self.credentials["username"]))

	def test_et_02_not_turn(self):
		# Ensure it is player two's turn
		self.game.user_turn = self.user2
		self.game.save()

		self.helper_execute_failure(self.et_cmd, "Please wait until it is your turn.")

	def test_et_03_success(self):
		# Simulate all units on other player's team having moved
		user2 = Users.objects.filter(username=self.credentials2["username"]).first()
		Unit.objects.filter(owner=user2, game=self.game).update(acted=True)

		self.helper_execute_success(self.et_cmd)

		# Ensure it is now user two's turn
		game = Game.objects.filter(pk=self.game.id).first()
		self.assertEqual(game.user_turn, self.user2)

		# Ensure each of the user two units can move
		units = Unit.objects.filter(owner=self.user2, game=game).exclude(hp__lte=0)
		for unit in units:
			self.assertFalse(unit.acted)