"""
.. module:: userhelper
   :synopsis: This file is used to store all methods helping with the processing of user objects

.. moduleauthor:: Drew, Brennan, and Nick

"""
from User.models import Users
from passlib.hash import bcrypt
import logging
import uuid

def encrypt(password):
	"""
	Encrypt the inputted passord
	"""
	return bcrypt.encrypt(password, rounds=12)

def verifyPassword(password, dbHash):
	"""
	Verify that a hashed password matches its database-stored hash value
	"""
	return bcrypt.verify(password, dbHash)

def generateLoginToken(user):
	"""
	Generates and saves a login token for a particular user.
	This function should validate the token hasn't been taken before assigning it to a user.

	:type user: User
	:param user: The user whose login token is to be updated

	:rtype: String
	:returns: The token set to that user
	"""
	tokenTaken = True
	maxAttempts = 20
	attempt = 0
	while tokenTaken and attempt < maxAttempts:
		token = uuid.uuid4().hex

		# Check to see if a user already has the generated token and retry if their is a match
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
	"""
	Creates a user with the provided values

	:type username: String
	:param username: The username for the user

	:type password: String
	:param password: The password to be hashed for the user

	:type email: String
	:param email: The email address the user has provided

	:rtype: User
	:return: A user object representing the new user
	"""

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