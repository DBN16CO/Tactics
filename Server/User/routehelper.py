"""
This file will handle all routed methods managing static data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command
as well as any other necessary information regarding the command.
"""
import logging
import User.userhelper
from User.models import Users
from Communication.routehelper import *
from fcm_django.models import FCMDevice
from Server.settings import ALLOWED_USER_PREFS, SUPPORTED_DEVICE_TYPES

def login(data):
	"""
	Login either with username/password or token

	Command: LGN (Login)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             	"username":"CoolUserName",\n
	             	"pw":"12345"\n
	             }\n
	             -- OR --\n
	             {\n
	             	"token":"dklaf00hdskalfhdsfsdf"\n
	             }\n

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True, "Token":"dklaf00hdskalfhdsfsdf","Username":"CoolUserName"}\n
				 If Unsuccessful:\n
				 {"Successful":False,"Error":"Invalid Username/Password."}\n
				 Notes:\n
				 	- The error message provided should be of an acceptable form such that
				 	  errors can be directly displayed for the user.
	"""
	username = None
	token = None
	user = None

	if "username" in data and "pw" in data:
		username = data["username"]
		password = data["pw"]

		user = Users.objects.filter(username=username).first()
		if user:
			verified = User.userhelper.verifyPassword(password, user.password)
			if verified:
				User.userhelper.refreshChannel(user, data['channel_name'])
				return {"Success": True, "Token": User.userhelper.generateLoginToken(user), "Username": user.username}

	elif "token" in data:
		token = data['token']
		user = Users.objects.filter(token=token).first()

		if user:
			isExpired = User.userhelper.isTokenExpired(user)
			if isExpired:
				return {"Success": False, "Error": "Login token has expired, please login again using your username/password."}

			User.userhelper.refreshChannel(user, data['channel_name'])
			User.userhelper.refreshToken(user)

			return {"Success": True, "Token": token, "Username": user.username}

	return {"Success": False, "Error": "Invalid Username/Password."}

def createUser(data):
	"""
	Create a user with the provided credentials

	Command: CU (Create User)

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             	"username":"CoolUserName",\n
	             	"pw":"12345",\n
	             	"email":"lameEmail@email.com"\n
	             }\n

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call:\n
				 If Successful:\n
				 {"Success":True, "Token":"dklaf00hdskalfhdsfsdf","Username":"CoolUserName"}\n
				 If Unsuccessful:\n
				 {"Successful":False,"Error":"Invalid Username/Password."}\n
				 Notes:\n
				 	- The error message provided should be of an acceptable form such that
				 	  errors can be directly displayed for the user.
	"""

	# Parse the necessary JSON values and validate
	error = None

	if not "username" in data:
		error = "No username was provided."
	elif not "pw" in data:
		error = "No password was provided."
	elif not "email" in data:
		error = "No email address was provided."

	if error:
		return formJsonResult(error)

	username = data["username"]
	pw		 = data["pw"]
	email	 = data["email"]

	# Try to add the user to the database
	try:
		usr1 = User.userhelper.createUser(username, pw, email, data['channel_name'])
	except Exception, e:
		logging.error("Error occurred while creating user:" + str(e))
		error = str(e)
		if "duplicate key value violates " in str(e):
			if "User_users_username_key" in str(e):
				error = "That username already exists."
			elif "User_users_email_key" in str(e):
				error = "That email is already in use."

		return formJsonResult(error)

	# Verify that the user was added
	usr2 = Users.objects.filter(username=username).first()
	if usr1 == usr2:
		response = {"Success": True, "Token": User.userhelper.generateLoginToken(usr2), "Username": usr2.username}
	else:
		response = {"Success": False}

	# Return the success message
	return response

def getUserInfo(data):
	"""
	Called to obtain all user-related data. This will likely be called once by the front end after login.

	Command: GUI (Get User Info)

	:type data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             }\n

	:rtype: Dictionary
	:return: A JSON object containing all of the user's information and preferences

			 {\n
			  "Success":True,\n
			  "Username":"<username>",\n
			  "Email":"<Email>",\n
			  "Verified":<True/False>,\n
			  "Level":<level>,\n
			  "Experience":<exp>,\n
			  "Coins":<num_coins>,\n
			  "Preferences": {"Grid Opacity":<opacity>, ...}\n
			 }\n
	"""
	username = data["session_username"]
	user = Users.objects.filter(username=username).first()

	response = {}

	if not user:
		return {"Success": False, "Error": "Unable to retrieve the user information from database"}

	response["Success"] = True
	response["Username"] = user.username
	response["Email"] = user.email
	response["Verified"] = user.verified
	response["Level"] = user.level
	response["Experience"] = user.experience
	response["Coins"] = user.coins
	response["Preferences"] = user.prefs

	return response

def sendUserInfo(data):
	"""
	Called to send user information to store on the server.
	Examples are the front end sending any user setting changes, usage statistics, and the GCM registration id.

	Command: SUI (Send User Info)

	:type data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	              "Preferences": {...},\n
	              "Notifications": {\n
					"RegistrationID": "<reg id>",\n
					"DeviceType": "android/ios",\n
	              }\n,
	              "Usage": {...} (Eventually)\n
	             }\n

	:rtype: Dictionary
	:return: A JSON object indicating whether the server successfully received and processed the data

			 {\n
			  "Success":True/False,\n
			  "Error": ""\n
			 }\n
	"""

	response = {"Success": True}

	username = data["session_username"]
	user = Users.objects.filter(username=username).first()

	gcm_settings = data.get('Notifications')

	if gcm_settings:
		reg_id = gcm_settings.get('RegistrationID')
		device_type = gcm_settings.get('DeviceType')

		if reg_id is None:
			error = "Notification Registration ID is missing for GCM Settings"
			return formJsonResult(error)

		if device_type is None:
			error = "Notification Device type is missing for GCM Settings"
			return formJsonResult(error)

		if device_type not in SUPPORTED_DEVICE_TYPES:
			error = "Device type '{}' is not supported for notifications".format(device_type)
			return formJsonResult(error)

		device = FCMDevice()
		device.registration_id = reg_id
		device.type = device_type
		device.save()

		user.device = device
		user.save()

	prefs = data.get('Preferences')

	if prefs:
		for pref in prefs:
			if pref not in ALLOWED_USER_PREFS:
				error = "User preference '{}' is not a known preference.".format(pref)
				return formJsonResult(error)

		user.prefs.update(prefs)
		user.save()

	return response