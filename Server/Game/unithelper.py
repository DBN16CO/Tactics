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
	return False

def validateMove(unit, game, newX, newY):
	return False
