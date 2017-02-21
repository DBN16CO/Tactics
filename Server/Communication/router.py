"""
.. module:: router
   :synopsis: Receives any JSON input from the front end and routes it to the proper application for processing

.. moduleauthor:: Drew, Brennan, and Nick
"""
import json
import logging

from User.models import Users
from Static.models import Version
import Game.routeunithelper
import Game.routegamehelper
import Game.unithelper
import Game.maphelper
import User.routehelper
import User.userhelper
import Static.routehelper
import Communication.routehelper

from channels.sessions import channel_session

def connect(message):
	message.reply_channel.send({
		"accept": True
	})

@channel_session
def processRequest(message):
	"""
	Communicates with the front end by sending and receiving JSON through a channel session

	:type message: Channel Object
	:param message: The message being received from the front end

		The following commands have been implemented:

		+-------+------------------+---------+--------------------+----------------------+
		| Abrev | Command Name     | App     | Method Name        | Test Class           |
		+=======+==================+=========+====================+======================+
		| CS    | Cancel Search    | Game    | cancelSearch       | TestFindMatch        |
		+-------+------------------+---------+--------------------+----------------------+
		| CU    | Create User      | User    | createUser         | TestCreateUser       |
		+-------+------------------+---------+--------------------+----------------------+
		| ET    | End Turn         | Game    | endTurn            | TestEndTurn          |
		+-------+------------------+---------+--------------------+----------------------+
		| FM    | Find Match       | Game    | findGame           | TestFindMatch        |
		+-------+------------------+---------+--------------------+----------------------+
		| GUI   | Get User Info    | User    | getUserInfo        | TestLoginLogout      |
		+-------+------------------+---------+--------------------+----------------------+
		| IL    | Iniitial Load    | Static  | getAllStaticData   | TestStatic           |
		+-------+------------------+---------+--------------------+----------------------+
		| LGN   | Login            | User    | login              | TestLoginLogout      |
		+-------+------------------+---------+--------------------+----------------------+
		| PA    | Ping Auth        | Comm    | pingAuthentication |                      |
		+-------+------------------+---------+--------------------+----------------------+
		| PU    | Place Units      | Game    | placeUnits         | TestPlaceUnits       |
		+-------+------------------+---------+--------------------+----------------------+
		| QGU   | Query Games User | Game    | queryGamesUser     | TestQueryGames       |
		+-------+------------------+---------+--------------------+----------------------+
		| ST    | Set Team         | Game    | setTeam            | TestSetTeam          |
		+-------+------------------+---------+--------------------+----------------------+
		| TA    | Take Action      | Game    | takeAction         | TestTakeAction       |
		+-------+------------------+---------+--------------------+----------------------+

		Notes about table above:\n
		- To find the documentation on the command, go to ../<App>/routehelper.<Method Name>\n
		- For an example input and output JSON, go to ../<App>/tests.testN_<Successful Test>

	:rtype: Dictionary
	:return: A response to the incoming request from the front end
	"""
	# Get the request
	request = message.content['bytes']
	logging.debug("Parsing incoming json request: \n{0}".format(request))

	# Parse the Json
	try:
		data = json.loads(request)
	except Exception, e:
		logging.exception(e)
		message.reply_channel.send({
			'text': json.dumps({"Success":False, "Error":"Input JSON invalid."})
		})
		return

	# Send keepalive message if the message contained a PING
	if "PING" in data:
		message.reply_channel.send({
			'text': json.dumps({"PONG":"PONG"})
			})
		return

	if not "Command" in data:
		logging.debug("Missing Command Key: {0}".format(data))
		message.reply_channel.send({
			'text': json.dumps({"Success":False,
				"Error":"The command information is incomplete."})
		})
		return

	cmd = data["Command"]
	logging.debug("Received command: " + str(cmd))

	# Obtain username if user is authenticated
	user = None
	if 'user' in message.channel_session:
		user = message.channel_session['user']

	# If the user is not authenticated
	if not user:
		if cmd != 'LGN' and cmd != 'CU':
			message.reply_channel.send({
			'text': json.dumps({"Success": False,
				"Error": "User is not authenticated, please login."})
			})
			return
	else:
		data['session_username'] = user

	# If the user is authenticated and the command is LGO, delete the session and return success
	if cmd == 'LGO':
		message.channel_session['user'] = None
		try:
			dbUser = Users.objects.filter(username=user).first()
			dbUser.token = None
			dbUser.save()
			response = {"Success": True}
		except Exception, e:
			logging.error("Database update to remove the user's login token failed: {0}".format(e))
			response = {"Success": False, "Error": "Internal Server Error during logout"}

		message.reply_channel.send({
			'text': json.dumps(response)
		})
		return

	# If the command is one of the following, it will also need the channel name for processing
	commands_needing_channel_name = ["FM",]
	if cmd in commands_needing_channel_name:
		data['channel_name'] = message.reply_channel.name
		logging.debug("Adding channel name to JSON: " + data['channel_name'])

	# If the command is one of the following, it will also need to ensure that the map version is initialized
	commands_needing_map_data = ["PU","TA"]
	if cmd in commands_needing_map_data:
		version_name = Version.objects.latest('pk').name
		if not version_name in Game.maphelper.maps:
			Game.maphelper.loadMaps(version_name)

	# Start processing the request
	commands={
		"CS":Game.routegamehelper.cancelSearch,
		"CU":User.routehelper.createUser,
		"ET":Game.routegamehelper.endTurn,
		"FM":Game.routegamehelper.findMatch,
		"GUI":User.routehelper.getUserInfo,
		"IL":Static.routehelper.getAllStaticData,
		"LGN":User.routehelper.login,
		"PA":Communication.routehelper.pingAuthentication,
		"PU":Game.routegamehelper.placeUnits,
		"QGU":Game.routegamehelper.queryGamesUser,
		"ST":Game.routeunithelper.setTeam,
		"TA":Game.routeunithelper.takeAction,
	}

	# Ensure that the command exists in the list of valid commands
	if not cmd in commands:
		response = {"Success":False, "Error": "Invalid command."}
		message.reply_channel.send({
			'text': json.dumps(response)
		})
		return

	try:
		response = commands[cmd](data)
	except Exception, e:
		logging.error("Failed to execute command: {0}".format(cmd))
		logging.debug(data)
		logging.exception(e)
		response = {"Success": False, "Error": "Internal Server Error."}

	# If the requested command was to create a new user or login to an existing user, set the channel session
	if "Success" in response and response['Success'] and (cmd == 'LGN' or cmd == 'CU'):
		message.channel_session['user'] = response.pop('Username')

	# Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})