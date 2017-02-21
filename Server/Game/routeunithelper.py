"""
This file will handle all routed methods managing unit data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command
as well as any other necessary information regarding the command.

"""
import logging
import Game.unithelper
import Static.statichelper
from Communication.routehelper import formJsonResult
from Static.models import Version
from Game.models import Game_User, Unit
from User.models import Users

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

	# Get Version and Static data, for use in validation - if setting team, must be newest version
	version = Version.objects.latest('pk')
	stat_info = Static.statichelper.getAllStaticData(version)

	# Ensure that the 'Units' key exists' there were at least some units and a leader selected
	if not "Units" in data:
		error = "The unit information is incomplete."
	elif not "Perks" in data:
		error = "The perk information is incomplete."
	# Ensure the user selected the proper number of units - too many, cheater!
	elif len(data["Units"]) > version.unit_max:
		error = "Too many units have been selected ({0}).".format(len(data["Units"]))
	# Ensure the user selected the proper number of units - too few, oops, add a few!
	elif len(data["Units"]) < version.unit_min:
		error = "You must select at least {0} unit(s), {1} chosen.".format(version.unit_min,
			"none" if len(data["Units"]) == 0 else len(data["Units"]))
	# Ensure that at least a leader and ability were provided
	elif not "Leader" in data or not "Ability" in data:
		error = "The leader information is incomplete."
	# All expected JSON keys existed
	else:
		# Ensure that the leader and ability are names that exist in the DB
		if not data["Leader"] in stat_info["Leaders"]:
			error = "The leader information provided is invalid."
		# Ensure that the pair of leader+ability is a valid pair
		elif not data["Ability"] in stat_info["Leaders"][data["Leader"]]["Abilities"]:
			error = "The {0} cannot use the ability {1}.".format(
				data["Leader"], data["Ability"])
		else:
			# Get the leader ability object to set in the Game_User table
			leader_ability = stat_info["Leaders"][data["Leader"]]["Abilities"][data["Ability"]]

			# Add each of the valid units to a list
			units = []
			unit_errs = ''
			for unt_nam in data["Units"]:
				# If a unit name provided was not valid
				if not unt_nam in stat_info["Classes"]:
					unit_errs += unt_nam +","
				else:
					units.append(stat_info["Classes"][unt_nam]["Object"])

			# Add each of the valid perks to a list
			perks = []
			perk_errs = ''
			for prk_nam in data["Perks"]:
				# If a perk name provided was not valid
				if not prk_nam in stat_info["Perks"]:
					perk_errs += prk_nam +","
				else:
					perks.append(stat_info["Perks"][prk_nam]["Object"])

			# If some of the units provided were not valid names
			if len(unit_errs) != 0:
				unit_errs = unit_errs.strip(",")
				error = "The following are not valid unit selections: {0}".format(unit_errs)
			# If some of the perks provided were not valid names
			elif len(perk_errs) != 0:
				perk_errs = perk_errs.strip(",")
				error = "The following are not valid perk selections: {0}".format(perk_errs)
			# If too many perks were selected
			elif len(perks) > 3:
				error = "Too many perks have been selected ({0}).".format(len(perks))
			else:
				error = Game.unithelper.setTeam(leader_ability, perks, units, username, version)
					
	return formJsonResult(error, data)

def takeAction(data):
	"""
	Called when a user wants to take an action with a specific unit, such as
	attacking an opponent, healing an ally, or simply moving to a new location.
	Command: TA (Take Action)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
				 be of the following format:\n
				 {\n
					"Action":"Attack",\n
					"Game":"vs. opponent #1",\n
				 	"Unit":1,\n
				 	"X":3,\n
				 	"Y":4,\n
				 	"Target":9\n
				 }\n
				 Notes:\n
				 	- Action is the NAME of a valid action\n
				 	- The value for Unit and Target are the unit's ID\n
				 	- The X and Y values are the new location for the unit\n
				 	- Depending on the action, the Target may be optional\n
				 	- Both X AND Y are required

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {\n
				 	"Success":True\n
				 	"Unit"{\n
						"ID":1,\n
						"HP":10,\n
						"NewHP":10\n
				 	},\n
				 	"Target":{\n
						"ID":9,\n
						"HP":10,\n
						"NewHP":0\n
				 	}\n
				 }\n
				 Notes:\n
				 	- The "Target" object could be omitted if the action did not involve a target.\n
				 	- The HP for the unit could be omitted if the action is "Wait" or "Heal"\n
				 	- The HP is the previous HP
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"You did not provide the necessary information."}\n
				 Notes:\n
				 	- The error message provided should be of an acceptable form such that
				 	  errors can be directly displayed for the user.
	"""
	game_data = Game.unithelper.validateGameStarted(data)
	if "Error" in game_data:
		return formJsonResult(game_data["Error"], data)

	user = game_data["User"]
	game = game_data["Game"]
	version = game_data["Version"]

	stat_info = Static.statichelper.getAllStaticData(version)

	# Get the new coordinates for the action
	if not "X" in data or not "Y" in data:
		return formJsonResult("Internal Error: New location information incomplete.", data)
	x = data["X"]
	y = data["Y"]

	# Get the unit taking the action
	if not "Unit" in data:
		return formJsonResult("Internal Error: Unit Key missing.", data)
	unit_id  = data["Unit"]
	unit = Unit.objects.filter(pk=unit_id, game=game, owner=user).first()
	if unit == None:
		return formJsonResult("Internal Error: Specified unit ID not in game.", data)
	elif unit.acted:
		return formJsonResult("That unit has already acted this turn.", data)

	# The valid actions for a user in this version
	if not "Action" in data:
		return formJsonResult("Internal Error: Action Key missing.", data)
	elif not data["Action"] in stat_info["Classes"][unit.unit_class.name]["Actions"] or not stat_info["Classes"][unit.unit_class.name]["Actions"][data["Action"]]:
		return formJsonResult("The selected action is not valid.", data)

	# Ensure that the move is valid
	is_move_valid = Game.unithelper.validateMove(unit, game, user, x, y)
	if "Error" in is_move_valid:
		return formJsonResult(is_move_valid["Error"], data)

	# Create a dictionary to describe the action for the unit
	unit_dict = {"Unit":unit, "NewX":x, "NewY":y}

	# If the unit is just moving for their action
	if data["Action"] == "Wait":
		if not Game.unithelper.saveActionResults(data["Action"], game, unit_dict):
			return formJsonResult("There was a problem executing the action.", data)
		action_result = {}
		action_result["Unit"] = unit_dict
		action_result["Unit"]["ID"] = action_result["Unit"]["Unit"].id

	# If the action is one that requires a target
	else:
		# Determine the target
		if not "Target" in data:
			return formJsonResult("Internal Error: Target Key missing.", data)
		target_id = data["Target"]
		if target_id == unit_id:
			return formJsonResult("Cannot target self.", data)
		target = Unit.objects.filter(pk=target_id, game=game).first()
		if target == None:
			return formJsonResult("Internal Error: Specified target ID not in game.", data)

		# Process attacking and healing
		action_result = Game.unithelper.calculateActionResult(data["Action"], game, unit_dict, target)
		
		if "Error" in action_result:
			return formJsonResult(action_result["Error"], data)

		if not Game.unithelper.saveActionResults(data["Action"], game, action_result["Unit"], action_result["Target"]):
			return formJsonResult("There was a problem targeting that unit.", data)

		action_result["Target"].pop("Unit", None)

	# Prepare the response
	action_result["Unit"].pop("Unit", None)
	response = formJsonResult("")

	# The unit response
	response_unit = action_result["Unit"]
	response["Unit"] = response_unit

	# The target unit response, if there was one
	if "Target" in action_result:
		target_unit = action_result["Target"]
		response["Target"] = target_unit

	return response