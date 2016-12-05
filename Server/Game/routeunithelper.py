"""
This file will handle all routed methods managing static data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command 
as well as any other necessary information regarding the command.

"""
import logging
import Game.unithelper
from Communication.routehelper import formJsonResult
from Static.models import Ability, Class, Leader, Leader_Ability, Perk, Version

"""
def unitCreation(data):
	# INCOMPLETE - if not implemented when issue 52 is resolved, should be deleted

	# Parse the necessary JSON values and validate
	username  = data["session_username"]
	unitClass = data["class"]
	version   = data["v"]

	# Try to add the unit to the database
	error = None
	try:
		unit1 = Game.unithelper.createUnit(username, unitClass, version)
	except Exception, e:
		logging.error("Problem creating unit: " + str(e))
		error = str(e)
		response = {"Success": False,
					"Error": error}
		return response

	# Verify the unit was added
	if unit1.id > 0:
		response = {"Success": True,
					"uid": unit1.id}
	else:
		response = {"Success": False}

	return response
"""

def setTeam(data):
	"""
	Called when a user wants to set their team lineup before starting a game.
	Will store their unit selection as well as their leader, his ability, and the perk data
	Command: ST (Set team)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             	"Leader":"Sniper",\n
	             	"Ability":"Increased Range"\n
	             	"Units":["Archer","Archer","Mage","Flier","Swordsman","Swordsman","Swordsman","Swordsman"],\n
	             	"Perks":["Extra Money","Strong Arrows","Mountain Fighter"]\n
	             }\n
	             Notes:\n
	             	- All of the values provided for each key are the X{Name} chosen for that key.\n
	             	- If no perks are chosen an empty list should still still be sent for that key

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True}\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"You did not provide the necessary information."}\n
				 Notes:\n
				 	- The error message provided should be of an acceptable form such that
				 	  errors can be directly displayed for the user.
	"""
	username = data["session_username"]

	error = ""
	logging.debug(data)

	# Get Version data, for use in validation - if setting team, must be newest version
	version = Version.objects.latest('pk')

	# Ensure that the 'Units' key exists' there were at least some units and a leader selected
	if not "Units" in data:
		error = "The unit information is incomplete."
	elif not "Perks" in data:
		error = "The perk information is incomplete."
	# Ensure the user selected the proper number of units - too many, cheater!
	elif len(data["Units"]) > version.unit_count:
		error = "Too many units have been selected (" + str(len(data["Units"])) + ")."
	# Ensure the user selected the proper number of units - too few, oops, add a few!
	elif len(data["Units"]) < version.unit_count:
		error = ("You must select " + str(version.unit_count) + " units, only "
			+ str(len(data["Units"])) + " chosen.")
	# Ensure that at least a leader and ability were provided
	elif not "Leader" in data or not "Ability" in data:
		error = "The leader information is incomplete."
	# All expected JSON keys existed
	else:
		# Get the ability and leader data and validate it
		ability = Ability.objects.filter(version=version, name=data["Ability"]).first()
		leader = Leader.objects.filter(version=version, name=data["Leader"]).first()
		leader_ability = Leader_Ability.objects.filter(ability=ability, leader=leader, version=version).first()

		# Ensure that the leader and ability are names that exist in the DB
		if ability == None or leader == None:
			error = "The leader information provided is invalid."
		# Ensure that the pair of leader+ability is a valid pair
		elif leader_ability == None:
			error = "The " + leader.name + " cannot use the ability " + ability.name + "."
		else:
			# Add each of the valid units to a list
			units = []
			unit_errs = ''
			for unt_nam in data["Units"]:
				unit = Class.objects.filter(name=unt_nam, version=version).first()

				# If a unit name provided was not valid
				if unit == None:
					unit_errs += unt_nam +","
				else:
					units.append(unit)

			# Add each of the valid perks to a list
			perks = []
			perk_errs = ''
			for prk_nam in data["Perks"]:
				perk = Perk.objects.filter(name=prk_nam, version=version).first()

				# If a perk name provided was not valid
				if perk == None:
					perk_errs += prk_nam +","
				else:
					perks.append(perk)

			# If some of the units provided were not valid names
			if len(unit_errs) != 0:
				unit_errs = unit_errs.strip(",")
				error = "The following are not valid unit selections: " + unit_errs
			# If some of the perks provided were not valid names
			elif len(perk_errs) != 0:
				perk_errs = perk_errs.strip(",")
				error = "The following are not valid perk selections: " + perk_errs
			# If too many perks were selected
			elif len(perks) > 3:
				error = "Too many perks have been selected (" + str(len(perks)) + ")."
			else:
				error = Game.unithelper.setTeam(leader_ability, perks, units, username, version)
					
	return formJsonResult(error, data)

"""
def takeAction(data):
	# INCOMPLETE - if not implemented when issue 34 is resolved, should be deleted

	username = data["session_username"]
	unit_id  = data.get("unit")
	action   = data.get("actn")
	newX     = data.get("x")
	newY     = data.get("y")
	target   = data.get("tgt")

	error = None
	if unit_id == None or action == None:
		logging.error("TA: User ID was not provided." if unit_id == None else "TA: Action was not provided.")
		logging.error(data)
		error = "Internal error."
	else:
		try:
			unit1 = Game.unithelper.takeAction(unit_id, action, newX, newY, target)
		except Exception, e:
			error = str(e)


	if unit1.id > 0:
		response = {"Success": True}
	else:
		response = {"Success": False,
					"Error": error}

	return response
"""

"""
# Moves the unit to the desired location, if valid
def moveUnit(data):
	# INCOMPLETE - if not implemented when issue 34 is resolved, should be deleted

	# Parse the necessary JSON values and validate
	username = data["owner"]
	unit_id  = data["uid"]
	newX     = data["toX"]
	newY     = data["toY"]

	# Try to add the unit to the database
	error = None
	try:
		unit1 = Game.unithelper.moveUnit(username, unit_id, newX, newY)
	except Exception, e:
		logging.error("Problem moving unit: " + str(e))
		error = str(e)
		response = {"Success": False,
					"Error": error}
		return response

	# Verify the unit was added
	if unit1.x_pos == newX and unit1.y_pos == newY:
		response = {"Success": True,
					"uid": unit1.id}
	else:
		response = {"Success": False}

	return response
"""