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
import Game.unithelper
import User.routehelper
import User.userhelper
import Static.routehelper
import Communication.routehelper

from channels.sessions import channel_session

@channel_session
def processRequest(message):
	"""
	Communicates with the front end by sending and receiving JSON through a channel session

	:type message: Channel Object
	:param message: The message being received from the front end

					The following commands have been implemented:

					+-------+---------------+---------+--------------------+--------------------------------+
					| Abrev | Command Name  | App     | Method Name        | Successful Test                |
					+=======+===============+=========+====================+================================+
					| CU    | Create User   | User    | createUser         | create_user_success            |
					+-------+---------------+---------+--------------------+--------------------------------+
					| FM    | Find Match    | Game    | findGame           | find_game_success              |
					+-------+---------------+---------+--------------------+--------------------------------+
					| GUI   | Get User Info | User    | getUserInfo        | get_user_info_success          |
					+-------+---------------+---------+--------------------+--------------------------------+
					| IL    | Iniitial Load | Static  | getAllStaticData   | initial_load_v1_0              |
					+-------+---------------+---------+--------------------+--------------------------------+
					| LGN   | Login         | User    | login              | login_success_token            |
					+-------+---------------+---------+--------------------+--------------------------------+
					| PA    | Ping Auth     | Comm    | pingAuthentication |                                |
					+-------+---------------+---------+--------------------+--------------------------------+
					| ST    | Set Team      | Game    | setTeam            | set_team_valid_input           |
					+-------+---------------+---------+--------------------+--------------------------------+

					Notes about table above:\n
					- To find the documentation on the command, go to ../<App>/routehelper.<Method Name>\n
					- For an example input and output JSON, go to ../<App>/tests.testN_<Successful Test>

	
	:rtype: Dictionary
	:return: A response to the incoming request from the front end
	"""
	# Get the request
	request = message.content['bytes']
	logging.debug("Parsing incoming json request: ")
	logging.debug(str(request))

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
			'text': json.dumps({"Success": False, "Error": "User is not authenticated, please login."})
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
			logging.error("Database update to remove the user's login token failed: " + str(e))
			response = {"Success": False, "Error": "Internal Server Error during logout"}

		
		message.reply_channel.send({
		'text': json.dumps(response)
		})
		return

	# Start processing the request
	commands={"CU":User.routehelper.createUser,
			  "FM":Game.routegamehelper.findMatch,
			  "GUI":User.routehelper.getUserInfo,
			  "IL":Static.routehelper.getAllStaticData,
			  "LGN":User.routehelper.login,	
			  "PA":Communication.routehelper.pingAuthentication,
			  "ST":Game.routeunithelper.setTeam,
	#		  "TA":Game.routeunithelper.takeAction,
	#		  "UC":Game.routeunithelper.unitCreation,
	}
	
	try:
		response = commands[cmd](data)
	except Exception, e:
		logging.error("Failed to execute command " + str(cmd))
		logging.exception(e)
		response = {"Success": False, "Error": "Internal Server Error"}

	# If the requested command was to create a new user or login to an existing user, set the channel session
	if "Success" in response and response['Success'] and (cmd == 'LGN' or cmd == 'CU'):
		message.channel_session['user'] = response.pop('Username')
	
	# Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})
