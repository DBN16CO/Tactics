import json
import logging

def processRequest(message):
	#Get the request
	request = message.content['bytes']

	#Parse the Json
	try:
		logging.debug("Parsing incoming json request")
		data = json.loads(request)
	except Exception, e:
		logging.error(str(e))
		return

	#Send keepalive message if the message contained a PING
	if "PING" in data:
		message.reply_channel.send({
			'text': json.dumps({"PONG":"PONG"})
			})
		return

	#Start processing the request
	response = {"Success": True}

	#Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})