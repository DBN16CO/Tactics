"""
.. module:: routehelper
   :synopsis: Handles any router commands specific to the Communication class as well as \
   			  any helper methods that other Apps' route helper modules might need.

.. moduleauthor:: Drew, Brennan, and Nick
"""
import logging

def pingAuthentication(data):
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
	:return: The response which can be sent back to the front-end user.
			 Note: If the result is a success, additional values may need to be added \
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