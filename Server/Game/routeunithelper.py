import logging

import Game.unithelper 

"""
This file will handle all routed methods managing users
All methods must follow the following standards:

Inputs - they will all take in only two inputs, 
    the userID (ignore if it doesn't make sense), and the JSON data
    
Outputs - they will pass back a formatted JSON response object
    which will detail the success or failure of the command
    as well as any other necessary information regarding the command.
"""
# Creates a unit of given type for user
def unitCreation(data):
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

# Handles setting a team
def setTeam(data):
	username = data["session_username"]

	error = ""

	# Get Version data, for use in validation - if setting team, must be newest version
	version = Version.objects.latest('pk')

	# Ensure that the 'Units' key exists' there were at least some units and a leader selected
	if not "Units" in data:
		error = "There were no units selected in the team."
	# Ensure the user selected the proper number of units - too many, cheater!
	elif count(data["Units"] >= version.unit_count):
		error = "Too many units have been selected."
	# Ensure the user selected the proper number of units - too few, oops, add a few!
	elif count(data["Units"] <= version.unit_count):
		error = "You must select " + str(version.unit_count) + " units, only " 
			+ count(data["Units"]) + " were chosen."
	elif not "Leader" in data or not "Ability" in data:
		error = "The leader information was not properly set."
	else:
		pass
		# Look through all of the units for their 
	
	if len(error) == 0:
		response = {"Success":True}
	else:
		response = {"Success":False,
					"Error":error}

	return response


# Handles any action a single unit can take
def takeAction(data):
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
# Moves the unit to the desired location, if valid
def moveUnit(data):
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