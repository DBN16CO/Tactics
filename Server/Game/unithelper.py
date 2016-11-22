import logging
from Game.models import Game, Unit
from Static.models import Action, Class, Stat, Version
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




def validateMove(unit, game, newX, newY):
	return False
