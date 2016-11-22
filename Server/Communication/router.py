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
	#Get the request
	request = message.content['bytes']

	#Parse the Json
	try:
		logging.debug("Parsing incoming json request: ")
		data = json.loads(request)
		logging.debug(str(data))
	except Exception, e:
		logging.error(str(e))
		return

	#Send keepalive message if the message contained a PING
	if "PING" in data:
		message.reply_channel.send({
			'text': json.dumps({"PONG":"PONG"})
			})
		return

	cmd = data["Command"]
	logging.debug("Received command: " + str(cmd))

	#Obtain username if user is authenticated
	user = None
	if 'user' in message.channel_session:
		user = message.channel_session['user']

	#If the user is not authenticated
	if not user:
		if cmd != 'LGN' and cmd != 'CU':
			message.reply_channel.send({
			'text': json.dumps({"Success": False, "Error": "User is not authenticated, please login."})
			})
			return
	else:
		data['session_username'] = user

	# Start processing the request
	commands={"CU":User.routehelper.createUser,
			  "LGN":User.routehelper.login,	
			  "IL":Static.routehelper.getAllStaticData,
			  "UC":Game.routeunithelper.unitCreation,
			  "TA":Game.routeunithelper.takeAction,
			  "PA":Communication.routehelper.pingAuthentication,
	}
	
	response = commands[cmd](data)

	#If the requested command was to create a new user or login to an existing user, set the channel session
	if "Success" in response and response['Success'] and (cmd == 'LGN' or cmd == 'CU'):
		message.channel_session['user'] = response.pop('Username')
	
	#Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})
