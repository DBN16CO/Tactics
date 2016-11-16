#from ..Static.models import Class, Stat, Version
from User.models import Users
from passlib.hash import bcrypt
import logging

""" 
This file is used to store all methods helping with the processing of user objects
"""

def encrypt(password):
	return bcrypt.encrypt(password, rounds=12)

def verifyPassword(password, dbHash):
	return bcrypt.verify(password, dbHash)

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