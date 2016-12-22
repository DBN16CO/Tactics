"""
This file will handle all routed methods managing game data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command
as well as any other necessary information regarding the command.

"""
import logging
from Communication.routehelper import formJsonResult
from Static.models import Version
from Game.models import Unit, Game_Queue, Game_User
import Game.unithelper
from User.models import Users

def findMatch(data):
	"""
	Called when the user is ready to start a game with their set team and find a game which will find a map and an opponent.
	Command: FM (Find Match)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             }\n
	             Notes:\n
	             	- Assumes the user has already set their team information (See Set Team in routeunithelper)\n
					- Requires the channel name be inserted to the above JSON

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True\n
				 }\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"You did not provide the necessary information."}\n
	"""
	error = ''

	user = Users.objects.filter(username=data["session_username"]).first()
	version = Version.objects.latest('pk')

	# Ensure that the user has set a team
	unitCount = Unit.objects.filter(owner=user, version=version, game=None).count()
	if unitCount != version.unit_count:
		logging.error(str(data["session_username"]) + "'s unit count is " + str(unitCount) + " when it should be " + str(version.unit_count) + ".")
		error = "You must set a team before starting a match."
	else:
		# Add the user to the game queue
		game_queue = Game_Queue(user=user, channel_name=data['channel_name'])
		game_queue.save()

	return formJsonResult(error)

def placeUnits(data):
	"""
	Called when the game is ready to start and the user is deciding where to place their units. 
	Command: PU (Place Units)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
				 be of the following format:\n
				{\n
					"Game":"vs. opponent #1",\n
					"Units":[\n
						{"Name":"Archer", "X":1,"Y":1},\n
						{"Name":"Archer", "X":2,"Y":3},\n
						{"Name":"Flier",  "X":1,"Y":2},\n
						...\n
					]\n
				}\n
				Notes:\n
					- The units listed must match those from set team, but the order does not matter

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True\n
				 }\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"You did not provide the necessary information."}\n
	"""
	user = Users.objects.get(username=data["session_username"])
	version = Version.objects.latest('pk')
	error = ''

	# Ensure that the game key exists
	if not "Game" in data:
		error = "Internal Error: Game key missing."
		return formJsonResult(error, data)
	elif not "Units" in data:
		error = "Internal Error: Unit key missing."
		return formJsonResult(error, data)

	game_name = data["Game"]
	unit_list = data["Units"]

	if len(unit_list) != version.unit_count:
		error = "Not enough units selected: (" + str(version.unit_count) + ") required, (" + str(len(unit_list)) + ") chosen."
		return formJsonResult(error, data)

	# Ensure that the game name provided is valid
	game_user_obj = Game_User.objects.filter(user=user, name=game_name).first()
	if game_user_obj == None:
		error = "Invalid game name (" + game_name + ") for user " + user.username + "."
	else:
		error = Game.unithelper.placeUnits(game_user_obj, unit_list, user, version)

	return formJsonResult(error, data)