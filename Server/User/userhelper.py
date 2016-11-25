#from ..Static.models import Class, Stat, Version
from User.models import Users
from passlib.hash import bcrypt
import logging
import uuid

""" 
This file is used to store all methods helping with the processing of user objects
"""

def encrypt(password):
	return bcrypt.encrypt(password, rounds=12)

def verifyPassword(password, dbHash):
	return bcrypt.verify(password, dbHash)

def generateLoginToken(user):
	tokenTaken = True
	maxAttempts = 20
	attempt = 0
	while tokenTaken and attempt < maxAttempts:
		token = uuid.uuid4().hex
		conflictUser = Users.objects.filter(token=token).first()
		if not conflictUser:
			user.token = token
			user.save()
			tokenTaken = False

		attempt += 1

	if tokenTaken:
		logging.error("Login Token Generation Failed: 20 Attempts to generate a random token resulted in user conflicts")

	return user.token

# Creates a user with the provided values
def createUser(username, password, email):
	#TODO Create validation for user values
	
	#TODO encrypt the password
	encryptPass = encrypt(password)
	logging.debug(encryptPass)

	# Create the user
	newUser = Users(username=username, password=encryptPass, email=email)
	newUser.save()

	#TODO Logic for verifying email
	
	# Return the user
	return newUser