import logging
import User.userhelper
from User.models import Users

"""
This file will handle all routed methods managing users
All methods must follow the following standards:

Inputs - they will all take in only two inputs, 
    the userID (ignore if it doesn't make sense), and the JSON data

Outputs - they will pass back a formatted JSON response object
    which will detail the success or failure of the command
    as well as any other necessary information regarding the command.
"""

# Login either with username/password or token
def login(data):
	username = None
	pw = None
	token = None
	user = None

	if "username" in data and "pw" in data:
		username = data["username"]
		password = data["pw"]

		user = Users.objects.filter(username=username).first()
		if user:
			verified = User.userhelper.verifyPassword(password, user.password)
			if verified:
				return {"Success": True, "Token": User.userhelper.generateLoginToken(user), "Username": user.username}

	elif "token" in data:
		token = data['token']
		user = Users.objects.filter(token=token).first()

		if user:
			return {"Success": True, "Token": token, "Username": user.username}
		
	return {"Success": False, "Error": "Invalid Username/Password"}


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
			else:
				error = str(e)

		response = {"Success": False,
					"Error": error}
		return response

	# Verify that the user was added
	usr2 = Users.objects.filter(username=username).first()
	if usr1 == usr2:
		response = {"Success": True, "Token": User.userhelper.generateLoginToken(usr2), "Username": usr2.username}
	else:
		response = {"Success": False}

	# Return the success message
	return response