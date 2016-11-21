import json
import logging

from User.models import Users
import Game.routeunithelper
import Game.unithelper
import User.routehelper
import User.userhelper
import Static.routehelper

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

	# TODO remove
	username = "archerowner"

	# Start processing the request
	commands={"CU":User.routehelper.createUser,
			  "IL":Static.routehelper.getAllStaticData,
			  "UC":Game.routeunithelper.unitCreation,
			  "TA":Game.routeunithelper.takeAction,
	}
	cmd = data["Command"]
	logging.debug("Received command: " + str(cmd))
	response = commands[cmd](username, data)
	
	#Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})
