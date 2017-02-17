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
	if unitCount < version.unit_min or unitCount > version.unit_max:
		logging.error("{0}'s unit count is {1} when it should be between {2} and {3}.".format(data["session_username"], unitCount, version.unit_min, version.unit_max))
		error = "You must set a team before starting a match."
	else:
		# Add the user to the game queue
		game_queue = Game_Queue(user=user, channel_name=data['channel_name'])
		game_queue.save()

	return formJsonResult(error)

def cancelSearch(data):
	"""
	Called when the user wants to cancel the game search.
	Note: This is a best effort attempt since it races the matchmaker.
	Command: CS (Cancel Search)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             }\n

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True\n
				 }\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"Failed to cancel the game search"}\n
	"""
	username = data['session_username']
	user = Users.objects.filter(username=username).first()
	in_game_queue = Game_Queue.objects.filter(user=user).first()

	error = ''
	if in_game_queue:
		logging.info("User ({0}) is in the game queue...deleting queue entry".format(username))
		try:
			in_game_queue.delete()
		except Exception as e:
			is_in_queue = Game_Queue.objects.filter(user=user).first() != None
			if is_in_queue:
				error = "Failed to cancel the game search"
				logging.exception(e)
			else:
				logging.info("User ({0}) was taken out of queue before delete could occur".format(username))
	else:
		logging.warning("User ({0}) requested to cancel game search but was not in the queue".format(username))

	return formJsonResult(error)

def queryGamesUser(data):
	"""
	Called when the front end wants to refresh the game information for a user.
	Command: QGU (Query Games for User)

	:type data:  Dictionary
	:param data: The necessary input information to process the command should
				 be of the following format:\n
				 {\n
				 }\n

	:rtype: 	 Dictionary
	:return:	 A JSON object noting the success of the method call and the game information for the user\n
				 Example output JSON:
				{\n
					"Success": "True/False",\n
					"Games": [\n
					       {\n
					          "Name": "vs. (username) #1",\n
					          "Round": 1,\n
					          "Your_Turn": "True/False",\n
					          "Map": "(Map Name)",\n
					          "Finished": "True/False",\n
					          "Your_Team": "(Team # - Used if more than 1v1)",\n
					          "Enemy_Team": "(Team # - Used if more than 1v1)",\n
					          "Your_Units": [\n
					                {\n
					                   "ID": 1,\n
					                   "Name": "(Class)",\n
					                   "HP": 99,\n
					                   "Prev_HP": 109,\n
					                   "X": 7,\n
					                   "Y": 8,\n
					                }\n
					          ],\n
					          "Your_Leader": {\n
					               "Name": "(Leader Name)",\n
					               "Ability": "(Ability)"\n
					          },\n
					          "Your_Perks": [\n
					               {\n
					                   "Name": "(Perk 1)",\n
					                   "Tier": "(Tier)"\n
					               }\n
					          ],\n
					          "Enemy_Units": [\n
					               {\n
					                   "ID": 2,\n
					                   "Name": "(Class)",\n
					                   "HP": 99,\n
					                   "Prev_HP": 109,\n
					                   "X": 7,\n
					                   "Y": 8,\n
					               }\n
					          ],\n
					          "Enemy_Leader": {\n
					               "Name": "(Leader Name)",\n
					               "Ability": "(Ability)"\n
					          },\n
					          "Enemy_Perks": [\n
					               {\n
					                   "Name": "(Perk 1)",\n
					                   "Tier": "(Tier)"\n
					               }\n
					          ]\n
					       }\n
					],\n
					"In_Game_Queue": "True/False"\n
				}\n

	"""
	username = data['session_username']
	user = Users.objects.filter(username=username).first()
	in_game_queue = Game_Queue.objects.filter(user=user).first() != None
	response = {"Success": True, "Games": [], "In_Game_Queue": in_game_queue}

	try:

		my_game_users = Game_User.objects.filter(user=user)
		for game_user in my_game_users:
			game = game_user.game

			if not game:

				# User has set a team but hasn't serched for a game, skipping
				continue
			else:

				# Get the opponent user's game_user entry
				opp_game_user = Game_User.objects.filter(game=game).exclude(user=user).first()
				opp_user = opp_game_user.user

				# Start constructing the game object
				game_response = {}
				game_response["Name"] = game_user.name
				game_response["Round"] = game.game_round
				game_response["Your_Turn"] = game.user_turn == user
				game_response["Map"] = game.map_path.name
				game_response["Finished"] = game.finished
				game_response["Your_Team"] = game_user.team
				game_response["Enemy_Team"] = opp_game_user.team

				# Obtain unit information for both players of this game
				your_units = Unit.objects.filter(game=game).exclude(owner=opp_user)
				enemy_units = Unit.objects.filter(game=game).exclude(owner=user)

				game_response["Your_Units"] = []
				game_response["Enemy_Units"] = []

				# Store information about each of the player's units
				for your_unit in your_units:
					unit = {}
					unit["ID"] = your_unit.id
					unit["Name"] = your_unit.unit_class.name
					unit["HP"] = your_unit.hp
					unit["X"] = your_unit.x
					unit["Y"] = your_unit.y

					game_response["Your_Units"].append(unit)

				# Store information about each of the enemy's units
				for enemy_unit in enemy_units:
					unit = {}
					unit["ID"] = enemy_unit.id
					unit["Name"] = enemy_unit.unit_class.name
					unit["HP"] = enemy_unit.hp
					unit["X"] = enemy_unit.x
					unit["Y"] = enemy_unit.y

					game_response["Enemy_Units"].append(unit)

				# Store information about your leader
				your_leader_ability = game_user.leader_abil
				your_leader = your_leader_ability.leader

				# Store information about the enemy's leader
				enemy_leader_ability = opp_game_user.leader_abil
				enemy_leader = enemy_leader_ability.leader

				game_response["Your_Leader"] = {"Name": your_leader.name, "Ability": your_leader_ability.ability.name}
				game_response["Enemy_Leader"] = {"Name": enemy_leader.name, "Ability": enemy_leader_ability.ability.name}

				# Store information about your perks
				game_response["Your_Perks"] = [
					{"Name": None if game_user.perk_1 == None else game_user.perk_1.name, "Tier":1},
					{"Name": None if game_user.perk_2 == None else game_user.perk_2.name, "Tier":2},
					{"Name": None if game_user.perk_3 == None else game_user.perk_3.name, "Tier":3}
				]

				# Store information about the enemy's perks
				game_response["Enemy_Perks"] = [
					{"Name": None if opp_game_user.perk_1 == None else opp_game_user.perk_1.name, "Tier":1},
					{"Name": None if opp_game_user.perk_1 == None else opp_game_user.perk_2.name, "Tier":2},
					{"Name": None if opp_game_user.perk_1 == None else opp_game_user.perk_3.name, "Tier":3}
				]

				# Add the game object to the list of the user's games
				response["Games"].append(game_response)

	except Exception, e:
		logging.error("Exception in query games for user:")
		logging.exception(e)
		return formJsonResult("Internal Server Error")

	return response

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

	# Ensure that the game name provided is valid
	game_user_obj = Game_User.objects.filter(user=user, name=game_name).first()
	if game_user_obj == None:
		return formJsonResult("Invalid game name ({0}) for user {1}.".format(game_name, user.username))

	unit_list = data["Units"]
	units_set = Unit.objects.filter(game=game_user_obj.game, owner=user, x=-1, y=-1).count()

	# Ensure the user is setting the proper number of units
	if len(unit_list) != units_set:
		error = "Incorrect number of units selected: ({0}) required, ({1}) chosen.".format(units_set, len(unit_list))
		return formJsonResult(error, data)

	# Call place units
	error = Game.unithelper.placeUnits(game_user_obj, unit_list, user, version)

	return formJsonResult(error, data)

def endTurn(data):
	"""
	Called when the user has completed all of their desired moves for a turn and is ready
	to pass play over to the opponent
	Command: ET (End Turn)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
				 be of the following format:\n
				{\n
					"Game":"vs. opponent #1"\n
				}\n

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True\n
				 }\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"It is not your turn."}\n
	"""
	game_data = Game.unithelper.validateGameStarted(data)
	if "Error" in game_data:
		return formJsonResult(game_data["Error"], data)

	game = game_data["Game"]
	other_user = Game_User.objects.filter(game=game).exclude(user=game_data["User"]).first().user

	# Update the game to be the other user's turn
	game.user_turn = other_user
	game.save()

	# Update each of the opposing player's living units so that they can now move
	Unit.objects.filter(owner=other_user, game=game).exclude(hp__lte=0).update(acted=False)

	return formJsonResult(None, data)