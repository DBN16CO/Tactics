"""
.. module:: unithelper
   :synopsis: Handles any logic necessary to process commands received in routeunithelper,
   			  and any necessary JSON handling on the input should have already been completed
   			  in the calling module.

.. moduleauthor:: Drew, Brennan, and Nick

"""
import logging, math
from random import randint

from Game.models import Game, Game_User, Unit
from Static.models import Action, Class, Class_Action, Stat, Unit_Stat
from User.models import Users
import Game.maphelper

def placeUnits(game_user, units, user, version):
	"""
	Validates that the units provided can be placed at their desired location.
	Then it adds them to the database.

	:type game_user: Game_User object
	:param game_user: The mapping for the game for which this user is placing units.

	:type units: List<Dictionary>
	:param units: A list of all the units and the X and Y coordinates on which to place them.

	:type user: User object
	:param user: The user placing units

	:type version: Version object
	:param version: Holds any necessary version information needed for processing.

	:rtype: String
	:return: An error message if any part of the process were to fail.
	"""
	set_units = Unit.objects.filter(owner=user, game=game_user.game).order_by("unit_class__name")

	# Ensure that the list of units matches the number from the set team
	if len(units) != len(set_units):
		return "Must place (" + str(len(set_units)) + ") units, not (" + str(len(units)) + ")."

	# Loop over every object in the query set and update (without saving yet) the X, Y, and health
	placed_units = sorted(units, key=lambda k: k['Name'])
	class_max_hp = {}

	map_name = game_user.game.map_path.name
	version_map_data = Game.maphelper.maps[version.name][map_name]
	for unit in set_units:
		# Further checks that inputs are valid
		if placed_units[0]["Name"] != unit.unit_class.name:
			return "Can only place units selected for this game."

		if not "X" in placed_units[0] or not "Y" in placed_units[0]:
			return "Internal Error: Missing X or Y."

		# Further check that the game has started - ensure the user is on a team
		user_team = game_user.team
		if user_team == 0:
			return "You cannot place units until both players have set their teams."

		# Check that the specific location in the map is valid for placement
		if version_map_data[placed_units[0]["X"]][placed_units[0]["Y"]]["Placement"] != user_team:
			return "Location X:" + str(placed_units[0]["X"]) + " Y:" + str(placed_units[0]["Y"]) + " is not a valid placement location for a unit for your team."

		# Momentarily store class HP maxes, in case the unit is selected more than once
		if not unit.unit_class.name in class_max_hp:
			class_obj = Class.objects.filter(name=unit.unit_class.name, version=version).first()
			unit_hp_max = Stat.objects.filter(name="HP", version=version).first()
			class_max_hp[unit.unit_class.name] = Unit_Stat.objects.filter(unit=class_obj, stat=unit_hp_max, version=version).first().value

		# Update the DB with the unit placement
		unit.x = placed_units[0]["X"]
		unit.y = placed_units[0]["Y"]
		unit.hp = class_max_hp[unit.unit_class.name]
		unit.acted = False

		# To keep the 0th unit to match with the current unit iteration in set_untis
		del placed_units[0]

	# Save all of the updated units
	for unit in set_units:
		unit.save()


def setTeam(leader_ability, perks, units, username, version):
	"""
	Validates an inputted team a user has provided and then updates
	the database for that user.

	:type leader_ability: Leader_Ability
	:param leader_ability: The user's specified leader chosen and that leader's ability

	:type perks: List<Perk>
	:param perks: The user's specified perks chosen

	:type units: List<Unit>
	:param units: The user's specified units chosen

	:type username: String
	:param units: The user's username

	:type version: Version
	:param version: The object for the most current version

	:rtype: String
	:return: An empty string unless the information provided was invalid, \
			 in which case, an error message will be provided, including when:
			 - The user has gone over the price limit
	"""
	err_msg = ''

	# Ensure the user did not spend too much selecting a team
	price_max = version.price_max
	money_spent = 0
	for unit in units:
		money_spent += unit.price
	if money_spent > price_max:
		return "The selected team is " + str(money_spent - price_max) + " over the unit budget."

	# Get the user object from the username
	user = Users.objects.get(username=username)

	# Ensure the user has not already set a team, if so, clear it
	if Game_User.objects.filter(game=None, user=user).first() != None:
		logging.info(username + " has resubmitted their team information, clearing existing data.")
		Game_User.objects.filter(game=None, user=user).delete()
		Unit.objects.filter(owner=user, game=None).delete()

	# Create a game user object for the leader and perk information
	game_user = Game_User(user=user, leader_abil=leader_ability)

	# Add each of the perks
	tier_mapping = {
		1:None, 
		2:None, 
		3:None
	}
	for perk in perks:
		if tier_mapping[perk.tier] != None:
			return "Cannot select more than one tier {0} perk: {1}, {2}".format(
				perk.tier, tier_mapping[perk.tier].name, perk.name)

		tier_mapping[perk.tier] = perk

	game_user.perk_1 = tier_mapping[1]
	game_user.perk_2 = tier_mapping[2]
	game_user.perk_3 = tier_mapping[3]

	game_user.save()

	# Add each of the units
	for lst_unt in units:
		unit = Unit(unit_class=lst_unt, owner=user, version=version)
		unit.save()

	return err_msg

def calculateActionResult(action, game, unit_dict, target):
	"""
	Determine the result of the provided action

	:type action: String
	:param action: The action the unit is trying to take

	:type game: Game object
	:param game: The game in which the acting unit resides

	:type unit_dict: Dictionary
	:param unit_dict: Describes the acting unit, has the Unit object, current HP and its location

	:type target: Unit Object
	:param target: The target of this unit's action

	:rtype: Dictionary
	:return: The result of the action, will have a "Unit" and "Target" dictionary
	"""
	version = game.version
	clss = unit_dict["Unit"].unit_class
	tgt_clss = target.unit_class
	hp = Stat.objects.filter(name="HP", version=version).first()

	# Get attack range
	attack_range_stat = Stat.objects.filter(name="Attack Range", version=version)
	atk_rng = Unit_Stat.objects.filter(stat=attack_range_stat, unit=clss,
		version=version).first().value

	# Is the target close enough?
	distance = abs(unit_dict["NewX"] - target.x) + abs(unit_dict["NewY"] - target.y)
	logging.debug("Attempting action on target {} away (Range={}).".format(distance, atk_rng))
	if distance > atk_rng:
		return {"Error":"Must be within {} range.  Target is {} away.".format(int(atk_rng), distance)}

	# Set the previous HP for each unit
	tgt_prev_hp = target.hp
	tgt_hp_left = tgt_prev_hp
	unit_prev_hp = unit_dict["Unit"].hp
	unit_hp_left = unit_prev_hp

	# Get stat objects
	agility = Stat.objects.filter(name="Agility", version=version).first()
	intel = Stat.objects.filter(name="Intelligence", version=version).first()
	strength = Stat.objects.filter(name="Strength", version=version).first()
	luck = Stat.objects.filter(name="Luck", version=version).first()
	defense = Stat.objects.filter(name="Defense", version=version).first()
	resist = Stat.objects.filter(name="Resistance", version=version).first()

	# Determine attack or heal amount and the amount prevented by the target
	attackType = clss.attack_type
	if attackType == "Physical":
		amount = Unit_Stat.objects.filter(stat=strength, unit=clss, version=version).first().value
		prevent = Unit_Stat.objects.filter(stat=defense, unit=tgt_clss, version=version).first().value
	elif attackType == "Magical":
		amount = Unit_Stat.objects.filter(stat=intel, unit=clss, version=version).first().value
		prevent = Unit_Stat.objects.filter(stat=resist, unit=tgt_clss, version=version).first().value

	# Process unit's action upon target
	if action == "Attack":
		logging.debug("{}[{}] attacking {}".format(clss.name,unit_dict["Unit"].id, target.id))

		if unit_dict["Unit"].owner == target.owner:
			return {"Error":"Cannot attack your own units!"}
		elif tgt_prev_hp == 0:
			return {"Error":"You cannot attack dead units."}

		# Check for a missed attack
		unit_agil = Unit_Stat.objects.filter(stat=agility, unit=clss, version=version).first().value
		tgt_agil = Unit_Stat.objects.filter(stat=agility, unit=tgt_clss, version=version).first().value
		agil_val = max(0, ((tgt_agil - unit_agil) * 5 ) + 5)

		# Check for a critical hit
		unit_luck = Unit_Stat.objects.filter(stat=luck, unit=clss, version=version).first().value
		tgt_luck = Unit_Stat.objects.filter(stat=luck, unit=tgt_clss, version=version).first().value
		luck_val = max(0, ((unit_luck - tgt_luck) * 5 ) + 5)

		# If attack misses, skip this section for dealing damage to target
		if randint(0, 99) > agil_val:
			# If critting, double attack amount
			if randint(0, 99) < luck_val:
				logging.debug("The unit had a critical hit on the target!")
				amount = 2 * amount

			# Calculate result
			tgt_hp_left = max(0, tgt_prev_hp - max(0, (amount - prevent)))
		else:
			logging.debug("MISSED the target!")

		# Determine if there will be a counter attack
		# 1. Is the target within range?
		tgt_atk_rng = Unit_Stat.objects.filter(stat=attack_range_stat, unit=tgt_clss,
		version=version).first().value
		logging.debug("Attempting counter attack on unit {} away (Range={}).".format(distance, tgt_atk_rng))

		# 2. Did the target's counter miss?
		agil_val = max(0, ((unit_agil - tgt_agil) * 5 ) + 5)

		# 3. Can the target even attack?
		action = Action.objects.filter(version=version, name="Attack").first()
		canAttack = not Class_Action.objects.filter(version=version, clss=tgt_clss, action=action).first() == None

		if distance <= tgt_atk_rng and tgt_hp_left > 0 and randint(0, 99) > agil_val and canAttack:
			logging.debug("Target within range to counter attack.")

			attackType = tgt_clss.attack_type
			if attackType == "Physical":
				amount = Unit_Stat.objects.filter(stat=strength, unit=tgt_clss, version=version).first().value
				prevent = Unit_Stat.objects.filter(stat=defense, unit=clss, version=version).first().value
			elif attackType == "Magical":
				amount = Unit_Stat.objects.filter(stat=intel, unit=tgt_clss, version=version).first().value
				prevent = Unit_Stat.objects.filter(stat=resist, unit=clss, version=version).first().value

			luck_val = max(1, (((tgt_luck - unit_luck) * 5 ) + 5) / 2)

			# If critting, double attack amount
			if randint(0, 99) < luck_val:
				logging.debug("The the target got a crit in response. Ouch!")
				amount = 2 * amount

			unit_hp_left = max(0, unit_prev_hp - max(0, math.ceil((amount - prevent) / 2)))
		else:
			logging.debug("MISSED! Or out of range to counter.")

	elif action == "Heal":
		if unit_dict["Unit"].owner != target.owner:
			return {"Error":"Cannot heal the enemy units!"}
		elif unit_dict["Unit"].id == target.id:
			return {"Error":"That unit cannot heal itself."}

		# Ensure the target is not already at full health
		tgt_hp_max = Unit_Stat.objects.filter(stat=hp, unit=tgt_clss, version=version).first().value
		if tgt_hp_max == tgt_prev_hp:
			return {"Error":"Target already has full Health."}
		elif tgt_prev_hp == 0:
			return {"Error":"You cannot heal dead units."}

		tgt_hp_left = min(tgt_hp_max, tgt_prev_hp + max(0, (amount - prevent)))

	# Create the response object
	response = {}
	response["Unit"] = unit_dict
	response["Unit"]["ID"] = response["Unit"]["Unit"].id
	response["Unit"]["HP"] = unit_prev_hp
	response["Unit"]["NewHP"] = unit_hp_left
	response["Target"] = {"Unit":target,"ID":target.id, "HP":tgt_prev_hp, "NewHP":tgt_hp_left}

	logging.debug("Result: %s", response)

	return response

def saveActionResults(action, game, unit_dict, target_dict=None):
	"""
	Updates the game with the provided action

	:type action: Action object
	:param action: The action taken

	:type game: Game object
	:param game: The game being updated

	:type unit_dict: Dictionary
	:param unit_dict: Necessary components to describe the updated unit, should contain:\n
						- "Unit" which is the unit object\n
						- "NewX" which is the X coordinate to which the unit is moving\n
						- "NewY" which is the Y coordinate to which the unit is moving\n
						- "HP" if a target was specified, which is the old HP for this unit before the action
						- "NewHP" if a target was specified, which is the new HP for this unit after the action

	:type target_dict: Dictionary
	:param target_dict: Necessary components to describe the targeted unit,
						should have "Unit" and "HP" keys which act the same as those in the unit_dict

	:rtype: Boolean
	:return: True if the update was successful, False otherwise
	"""
	unit = unit_dict["Unit"]
	unit.x = unit_dict["NewX"]
	unit.y = unit_dict["NewY"]
	unit.acted = True

	# If there is not target
	if target_dict == None:
		unit.prev_target = None
		unit.save()
		return True

	# Information specific to having a target
	unit.target = target_dict["Unit"]
	unit.hp = unit_dict["NewHP"]
	if unit.hp <= 0:
		logging.debug("The attacking unit was KILLED by a counterattack.")
		unit.dead = True

	target = target_dict["Unit"]
	target.hp = target_dict["NewHP"]
	if target.hp <= 0:
		logging.debug("The target was KILLED!")
		target.dead = True

	# Save the result
	unit.save()
	target.save()

	# Reload the units and ensure the data was saved
	#TODO

	return True

def validateMove(unit, game, user, newX, newY):
	"""
	Using a modified BFS algorithm, ensures that the specified movement is a valid location for the specified unit

	:type unit: Unit object
	:param unit: The unit being moved

	:type game: Game object
	:param game: The game in which the unit exists

	:type user: User object
	:param user: The owner of the unit being moved

	:type newX: Integer
	:param newX: The X coordinate to which the unit is moving

	:type newY: Integer
	:param newY: The Y coordinate to which the unit is moving

	:rtype: Boolean
	:return: True if the movement is valid, false otherwise.
	"""
	unit_locations = {}
	other_units = Unit.objects.filter(game=game).exclude(pk=unit.pk)
	for unt in other_units:
		x = unt.x
		y = unt.y

		if not x in unit_locations:
			unit_locations[x] = {}

		if not y in unit_locations[x]:
			if unt.owner.pk == user.pk:
				unit_locations[x][y] = "Ally"
			else:
				unit_locations[x][y] = "Enemy"
		else:
			error = "Internal Error: Two units located on same token ({},{}).".format(x, y)
			return {"Error":error}
	logging.debug("Unit Locations %s", unit_locations)

	# Determine how far this unit can move
	version = game.version
	move_range = Unit_Stat.objects.filter(unit=unit.unit_class, version=version, stat=Stat.objects.filter(version=version, name="Move").first()).first().value
	logging.debug("Attempting to move %s from location (%d,%d) to location (%d,%d).", unit.unit_class.name, unit.x, unit.y, newX, newY)

	# Helper variables for next section of code
	map_data = Game.maphelper.maps[version.name][game.map_path.name]
	move_data = Game.maphelper.movement_dict
	class_name = unit.unit_class.name

	# Using BFS: Create a queue of valid tokens, if the queue is ever empty, the movement target was invalid
	# Requirements to add to the queue:
	# - Not occupied by enemy
	# - Adjacent token is valid on map
	# - Adjacent token can be moved to (remaining movement minus cost to move to adjacent)
	# - Token has not already been checked
	# May exit the queue early (With success) if the following are ALL met:
	# - Not occupied by ally
	# - Current X,Y equals target X,Y
	# Uses:
	# valid_move_queue - List of tokens to check in queue, has the X, Y, and the remaining movement range
	# checked_tokens_dict - Dictionary of checked tokens, to ensure the same token is not checked twice
	valid_move_queue = [{"X":unit.x, "Y":unit.y, "Remaining":move_range}]
	checked_tokens_dict = {unit.x:{unit.y:True}}
	while len(valid_move_queue) > 0:
		# Get next list element and prepare for processing
		token = valid_move_queue.pop(0)
		x = token["X"]
		y = token["Y"]
		logging.debug("Checking location (%d,%d).", x, y)

		# Ensure this token is not already occupied, if occupied by:
		if x in unit_locations and y in unit_locations[x]:
			# Enemy, skip token, cannot move here or through
			if unit_locations[x][y] == "Enemy":
				# If this is the target location, can fail early, cannot move to unit location
				if x == newX and y == newY:
					error = "Location ({},{}) occupied by an enemy. Cannot move to that token.".format(x, y)
					return {"Error":error}

				# Otherwise, just continue to the next token
				logging.debug("Location (%d,%d) occupied by enemy unit, skipping.", x, y)
				continue
			# Ally, do not check that this is end token, cannot end here
			else:
				if x == newX and y == newY:
					error = "Location ({},{}) occupied by an ally. Can move through, but not to, that token.".format(x, y)
					return {"Error":error}
		# Not currently occupied
		else:
			# Is this the target token
			if x == newX and y == newY:
				logging.debug("SUCCESS! Can move to (%d,%d).", x, y)
				return {"Success":True}

		# Calculate if the unit can move to adjacent tokens, and if so add to queue,
		# The four sets are for North, South, East, and West of the token, in that order
		for dX,dY in [(0,-1),(0,1),(1,0),(-1,0)]:
			deltX = x + dX
			deltY = y + dY

			# Ensure this token has not already been processed, and prevent this for future tokens
			if not deltX in checked_tokens_dict:
				checked_tokens_dict[deltX] = {}

			if deltY in checked_tokens_dict[deltX]:
				continue

			checked_tokens_dict[deltX][deltY] = True

			# If this new token is on the map
			if deltX in map_data and deltY in map_data[deltX]:
				next_ter_shortname = map_data[deltX][deltY]["Terrain"]
				move_cost = move_data[next_ter_shortname][class_name]
				rem_mvmt = token["Remaining"] - move_cost

				# If the unit can move to this location
				if rem_mvmt >= 0:
					valid_move_queue.append({"X":deltX,"Y":deltY,"Remaining":rem_mvmt})

	# If exited the while loop, target token was not found
	error = "Target location ({},{}) was out of reach for {} at location ({},{}).".format(newX, newY, class_name, unit.x, unit.y)
	return {"Error":error}

def validateGameStarted(data):
	"""
	Validates that the provided game name maps to a game that exists and has started

	:type data: Dictionary
	:param data: The provided dictionary of inputs, should include 'Game' and 'session_username'

	:rtype: Dictionary
	:return: A set of useful results gathered from getting the game, including: Game, user, game_user
	"""
	username = data["session_username"]
	user = Users.objects.filter(username=username).first()

	# Ensure that the game name provided is valid
	if not "Game" in data:
		return {"Error":"Internal Error: Game Key missing."}
	game_name = data["Game"]

	# Ensure that the game name matches with this user
	game_usr = Game_User.objects.filter(user=user, name=game_name).first()
	if game_usr == None:
		return {"Error":"No match for game of name {0}.".format(game_name)}

	version = game_usr.game.version

	# Now verify both players have placed their units
	game = game_usr.game
	user_placed_unit_count = Unit.objects.filter(game=game, owner=user).exclude(x=-1).exclude(y=-1).count()
	user_unplaced_unit_count = Unit.objects.filter(game=game, owner=user, x=-1, y=-1).count()
	opponent_placed_unit_count = Unit.objects.filter(game=game).exclude(x=-1).exclude(y=-1).exclude(owner=user).count()
	opponent_unplaced_unit_count = Unit.objects.filter(game=game, x=-1, y=-1).exclude(owner=user).count()
	expected_min = version.unit_min

	# All units are placed
	if user_unplaced_unit_count != 0:
		return {"Error":"You must place all of your units before taking a turn."}
	elif opponent_unplaced_unit_count != 0:
		return {"Error":"Please wait until your opponent places their units before taking a turn."}

	# Enough units are placed
	if user_placed_unit_count < expected_min or opponent_placed_unit_count < expected_min:
		return {"Error":"Internal Error: Teams were set with the incorrect team size."}

	# Now ensure that the proper team is acting
	if game.user_turn != user:
		logging.debug("{0} attempting to act when it is {1}'s turn.".format(user.username, game.user_turn.username))
		return {"Error":"Please wait until it is your turn."}

	# If it was successful, return the useful infomration collected
	return {
		"User":user,
		"Game":game,
		"Version":version
	}