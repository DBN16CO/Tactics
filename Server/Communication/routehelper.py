"""
This file will handle all routed methods managing static data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command 
as well as any other necessary information regarding the command.

"""
import logging

def pingAuthentication(data):
	"""
	A ping that ensures the user has been authenticated

	Command: PA (Ping Authentication)

	:type data: Dictionary
	:param data: The inputted JSON command which should include the 'session_username' provided  in :func:`processRequest`,
				 if not, then the session is invalid.

	:rtype: Dictionary
	:return: The response which can be sent back to the front end
	"""
	if "session_username" in data:
		return {"PONG_AUTH": "PONG_AUTH"}
	else:
		return {"Ruh Roh": "How did we get this far??"}

def formJsonResult(error_msg, data=None):
	"""
	Creates the basic response for any method that must return a JSON response.

	:type error_msg: String
	:param error_msg: The error message to be printed if the function did not execute sucessfuly.

	:type data: Dictionary
	:param data: The inputted JSON command data that resulted in an error.

	:rtype: Dictionary
	:return: The response which can be sent back to the front-end user.\n
			 Note: If the result is a success, additional values may need to be added
			 to the response dictionary.
	"""
	if len(error_msg) == 0:
		response = {"Success":True}
	else:
		log_msg = error_msg
		if data != None and len(data) != 0:
			log_msg += ":\n" + str(data)
		logging.error(log_msg)
		response = {"Success":False,
					"Error":error_msg}

	return response