import json
import logging

from User.models import Users
import Game.routeunithelper
import Game.unithelper
import User.routehelper
import User.userhelper

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

	# Start processing the request
	commands={"CU":User.routehelper.createUser,
			  "UC":Game.routeunithelper.unitCreation,
			  "TA":Game.routeunithelper.takeAction,
	}
	cmd = data["Command"]
	logging.debug("Received command: " + str(cmd))
	response = commands[cmd](data)
	
	#Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})
