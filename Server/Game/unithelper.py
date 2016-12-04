import logging
from Game.models import Game, Game_User, Unit
from Static.models import Action, Class, Hero_Ability, Leader, Leader_Ability, Perk, Stat, Version
from User.models import Users
import validation

""" 
This file is used to store all methods helping with the processing of unit objects
"""

# Creates a unit of the given type for the given player
def createUnit(ownr, clss, vrsn):
	# Get necessary values to create unit
	user_id = Users.objects.get(username=ownr).id
	ver_id  = Version.objects.get(name=vrsn).id
	clss_id = Class.objects.get(name=clss, version_id=ver_id).id
	hp_rem  = Stat.objects.get(unit=clss_id, name='HP', version_id=ver_id).value
	logging.debug("Ver id: " + str(ver_id) + " clss_id: " 
		+ str(clss_id) + " hp_rem: " + str(hp_rem) + " ownr_id: " + str(ownr))

	# Create and save the unit
	retUnit = Unit(unit_class_id=clss_id, hp_remaining=hp_rem, owner_id=user_id)
	retUnit.save()

	# Return the unit
	return retUnit

def takeAction(unitId, action, newX, newY, target):
	# Get the unit based on the ID provided
	unit = Unit.objects.get(pk=unitId)
	action_name = Action.objects.get(pk=action)

	# Ensure the unit is in a game
	if unit.game == None:
		logging.error("The specified unit (ID=" + str(unit.id) + ") is not in a game, trying to take an action.")
		return None

	# Get the game object
	game = Game.objects.get(pk=unit.game)

	# Validate the move
	if validateMove(unit, game, newX, newY) == False:
		return False

	# If the move was validated, make the move
	unit.prev_x = unit.x_pos
	unit.prev_y = unit.y_pos
	unit.x_pos  = newX
	unit.y_pos  = newY

	# Next, validate the action specified
	action_options={"Attack":validation.attack,
					"Heal":validation.heal,
					"Wait":validation.wait}

	# Lastly, save the result
	unit.save()

	return unit


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

def validateMove(unit, game, newX, newY):
	return False
