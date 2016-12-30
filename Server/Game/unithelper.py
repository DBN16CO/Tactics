"""
.. module:: unithelper
   :synopsis: Handles any logic necessary to process commands received in routeunithelper,
   			  and any necessary JSON handling on the input should have already been completed
   			  in the calling module.

.. moduleauthor:: Drew, Brennan, and Nick

"""
import logging
from Game.models import Game, Game_User, Unit
from Static.models import Action, Class, Stat, Unit_Stat, Version
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
		return "Must place (" + len(set_units) + ") units, not (" + len(units) + ")."

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

		# Check that the specific location in the map is valid for placement
		if version_map_data[placed_units[0]["X"]][placed_units[0]["Y"]]["Placement"] != "1":
			return "Location X:" + str(placed_units[0]["X"]) + " Y:" + str(placed_units[0]["Y"]) + " is not a valid placement location for a unit."

		# Momentarily store class HP maxes, in case the unit is selected more than once
		if not unit.unit_class.name in class_max_hp:
			class_obj = Class.objects.filter(name=unit.unit_class.name, version=version).first()
			unit_hp_max = Stat.objects.filter(name="HP", version=version).first()
			class_max_hp[unit.unit_class.name] = Unit_Stat.objects.filter(unit=class_obj, stat=unit_hp_max, version=version).first().value

		# Update the DB with the unit placement
		unit.x_pos = placed_units[0]["X"]
		unit.y_pos = placed_units[0]["Y"]
		unit.hp_remaining = class_max_hp[unit.unit_class.name]

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
	perk_count = len(perks)
	if perk_count > 0:
		game_user.perk_1 = perks[0]
	if perk_count > 1:
		game_user.perk_2 = perks[1]
	if perk_count > 2:
		game_user.perk_3 = perks[2]

	game_user.save()

	# Add each of the units
	for lst_unt in units:
		unit = Unit(unit_class=lst_unt, owner=user, version=version)
		unit.save()

	return err_msg

def calculateAttack(game, unit_dict, target):

	# Create the response object
	response = {}
	response["Unit"] = unit_dict
	response["Unit"]["ID"] = response["Unit"]["Unit"].id
	response["Unit"].pop("Unit", None)
	response["Target"] = {"ID":target.id}

	return response

def calculateHeal(game, unit_dict, target):

	# Create the response object
	response = {}
	response["Unit"] = unit_dict
	response["Unit"]["ID"] = response["Unit"]["Unit"].id
	response["Unit"].pop("Unit", None)
	response["Target"] = {"ID":target.id}

	return response

def updateValidAction(game, unit_dict, target_dict=None):
	"""
	Updates the game with the provided action

	:type game: Game object
	:param game: The game being updated

	:type unit_dict: Dictionary
	:param unit_dict: Necessary components to describe the updated unit, should contain:\n
						- "Unit" which is the unit object\n
						- "NewX" which is the X coordinate to which the unit is moving\n
						- "NewY" which is the Y coordinate to which the unit is moving\n
						- "HP" if a target was specified, which is the new HP for this unit after the action

	:type target_dict: Dictionary
	:param target_dict: Necessary components to describe the targeted unit, 
						should have "Unit" and "HP" keys which act the same as those in the unit_dict

	:rtype: Boolean
	:return: True if the update was successful, False otherwise
	"""
	unit = unit_dict["Unit"]
	unit.x_pos = unit_dict["NewX"]
	unit.y_pos = unit_dict["NewY"]
	logging.debug("SDFASDFADSFGADFSGADSFADSFA unit:%s, x:%d, y:%d",unit.unit_class.name, unit_dict["NewX"], unit_dict["NewY"])
	if target_dict == None:
		unit.save()
		return True

	# Target not yet implemented
	return False

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
		x = unt.x_pos
		y = unt.y_pos

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
	logging.debug("Attempting to move %s from location (%d,%d) to location (%d,%d).", unit.unit_class.name, unit.x_pos, unit.y_pos, newX, newY)

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
	valid_move_queue = [{"X":unit.x_pos, "Y":unit.y_pos, "Remaining":move_range}]
	checked_tokens_dict = {unit.x_pos:{unit.y_pos:True}}
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
	error = "Target location ({},{}) was out of reach for {} at location ({},{}).".format(newX, newY, class_name, unit.x_pos, unit.y_pos)
	return {"Error":error}