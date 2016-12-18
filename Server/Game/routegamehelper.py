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
from Game.models import Unit, Game_Queue
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
	             	- Assumes the user has already set their team information (See Set Team in routeunithelper)
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

	my_game_users = Game_User.objects.filter(user=user)
	for game_user in my_game_users:
		game = game_user.game

		if not game:
			continue
		else:
			opp_game_user = Game_User.objects.filter(game=game).exclude(user=user).first()
			opp_user = opp_game_user.user

			game_response = {}
			game_response["Name"] = game_user.name
			game_response["Round"] = game.game_round
			game_response["Your_Turn"] = game.user_turn == user
			game_response["Map"] = game.map_path.name
			game_response["Finished"] = game.finished
			game_response["Your_Team"] = game_user.team
			game_response["Enemy_Team"] = opp_game_user.team

			your_units = Unit.objects.filter(game=game).exclude(user=opp_user)
			enemy_units = Unit.objects.filter(game=game).exclude(user=user)

			game_response["Your_Units"] = []
			game_response["Enemy_Units"] = []

			for your_unit in your_units:
				unit = {}
				unit["Name"] = your_unit.unit_class.name
				unit["HP_Rem"] = your_unit.hp_remaining
				unit["Prev_HP"] = your_unit.prev_hp
				unit["X"] = your_unit.x_pos
				unit["Y"] = your_unit.y_pos
				unit["Prev_X"] = your_unit.prev_x
				unit["Prev_Y"] = your_unit.prev_y
				unit["Prev_Target"] = {}
				unit["Prev_Action"] = {}
				game_response["Your_Units"].append(unit)

			for enemy_unit in enemy_units:
				unit = {}
				unit["Name"] = enemy_unit.unit_class.name
				unit["HP_Rem"] = enemy_unit.hp_remaining
				unit["Prev_HP"] = enemy_unit.prev_hp
				unit["X"] = enemy_unit.x_pos
				unit["Y"] = enemy_unit.y_pos
				unit["Prev_X"] = enemy_unit.prev_x
				unit["Prev_Y"] = enemy_unit.prev_y
				unit["Prev_Target"] = {}
				unit["Prev_Action"] = {}
				game_response["Enemy_Units"].append(unit)

			your_leader_ability = game_user.leader_abil
			your_leader = your_leader_ability.leader

			enemy_leader_ability = opp_game_user.leader_abil
			enemy_leader = enemy_leader_ability.leader

			game_response["Your_Leader"] = {"Name": your_leader.name, "Ability": your_leader_ability.ability.name}
			game_response["Enemy_Leader"] = {"Name": enemy_leader.name, "Ability": enemy_leader_ability.ability.name}

			game_response["Your_Perks"] = [
				{"Name": game_user.perk_1.name, "Tier": game_user.perk_1.tier},
				{"Name": game_user.perk_2.name, "Tier": game_user.perk_2.tier},
				{"Name": game_user.perk_3.name, "Tier": game_user.perk_3.tier}
			]

			game_response["Enemy_Perks"] = [
				{"Name": opp_game_user.perk_1.name, "Tier": opp_game_user.perk_1.tier},
				{"Name": opp_game_user.perk_2.name, "Tier": opp_game_user.perk_2.tier},
				{"Name": opp_game_user.perk_3.name, "Tier": opp_game_user.perk_3.tier}
			]

			response["Games"].append(game_response)

	return response


def placeUnits(data):
	"""
	Called when the game is ready to start and the user is deciding where to place their units. 
	Command: PU (Place Units)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             }\n
	             Notes:\n
	             	- Assumes the user has already set their team information (See Set Team in routeunithelper)

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True\n
				 }\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"You did not provide the necessary information."}\n
	"""
	return False