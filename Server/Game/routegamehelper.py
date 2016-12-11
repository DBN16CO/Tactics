"""
This file will handle all routed methods managing game data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command
as well as any other necessary information regarding the command.

"""
import logging
import Game.unithelper
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

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True,\n
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
		logging.error(username + "'s unit count is " + str(unitCount) + " when it should be " + version.unit_count + ".")
		error = "You must set a team before starting a match."
	else:
		# Add the user to the game queue
		game_queue = Game_Queue(user=user)
		game_queue.save()

	return formJsonResult(error)
