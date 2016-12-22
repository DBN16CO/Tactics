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
					unit["HP_Rem"] = your_unit.hp_remaining
					unit["Prev_HP"] = your_unit.prev_hp
					unit["X"] = your_unit.x_pos
					unit["Y"] = your_unit.y_pos
					unit["Prev_X"] = your_unit.prev_x
					unit["Prev_Y"] = your_unit.prev_y
					
					prev_target = your_unit.prev_target
					prev_action = your_unit.prev_action
					if prev_target:
						unit["Prev_Target"] = prev_target.id
						unit["Prev_Action"] = prev_action.name
					else:
						unit["Prev_Target"] = None
						unit["Prev_Action"] = None

					game_response["Your_Units"].append(unit)

				# Store information about each of the enemy's units
				for enemy_unit in enemy_units:
					unit = {}
					unit["ID"] = enemy_unit.id
					unit["Name"] = enemy_unit.unit_class.name
					unit["HP_Rem"] = enemy_unit.hp_remaining
					unit["Prev_HP"] = enemy_unit.prev_hp
					unit["X"] = enemy_unit.x_pos
					unit["Y"] = enemy_unit.y_pos
					unit["Prev_X"] = enemy_unit.prev_x
					unit["Prev_Y"] = enemy_unit.prev_y

					prev_target = enemy_unit.prev_target
					prev_action = enemy_unit.prev_action
					if prev_target:
						unit["Prev_Target"] = prev_target.id
						unit["Prev_Action"] = prev_action.name
					else:
						unit["Prev_Target"] = None
						unit["Prev_Action"] = None

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
					{"Name": game_user.perk_1.name, "Tier": game_user.perk_1.tier},
					{"Name": game_user.perk_2.name, "Tier": game_user.perk_2.tier},
					{"Name": game_user.perk_3.name, "Tier": game_user.perk_3.tier}
				]

				# Store information about the enemy's perks
				game_response["Enemy_Perks"] = [
					{"Name": opp_game_user.perk_1.name, "Tier": opp_game_user.perk_1.tier},
					{"Name": opp_game_user.perk_2.name, "Tier": opp_game_user.perk_2.tier},
					{"Name": opp_game_user.perk_3.name, "Tier": opp_game_user.perk_3.tier}
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