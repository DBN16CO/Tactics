import json
import logging

from User.models import Users
import User.userhelper

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

	# Start processing the request
	commands={"CU":createUser,
			  "PU":placeUnit,
	}
	cmd = data["Command"]
	logging.debug("Received command: " + str(cmd))
	response = commands[cmd](data)
	
	#Reply back
	message.reply_channel.send({
		'text': json.dumps(response)
	})

"""
Below are the methods used to handle the routed commands,
they will all follow the following format:

Inputs - they will all take in only one input, the JSON data

Outputs - they will pass back a formatted JSON response object
    which will detail the success or failure of the command
    as well as any other necessary information regarding the command.
"""
# Creates a user with the given input values
def createUser(data):
	# Parse the necessary JSON values and validate
	username = data["username"]
	pw		 = data["pw"]
	email	 = data["email"]

	# Try to add the user to the database
	error = None
	try:
		usr1 = User.userhelper.createUser(username, pw, email)
	except Exception, e:
		logging.error("Error occurred while creating user:" + str(e))
		if "duplicate key value violates " in str(e):
			if "User_users_username_key" in str(e):
				error = "That username already exists."
			elif "User_users_email_key" in str(e):
				error = "That email is already in use."

		response = {"Success": False,
					"Error": error}
		return response

	# Verify that the user was added
	usr2 = Users.objects.get(username=username)
	if usr1 == usr2:
		response = {"Success": True}
	else:
		response = {"Success": False}

	# Return the success message
	return response


def placeUnit(data):
	return