"""
.. module:: userhelper
   :synopsis: This file is used to store all methods helping with the processing of user objects

.. moduleauthor:: Drew, Brennan, and Nick

"""
from User.models import Users
from passlib.hash import bcrypt
import logging
import uuid
import re
from django.utils import timezone
from Server.config import LOGIN_TOKEN_EXPIRATION, PASSWORD_POLICY

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

def refreshToken(user):
	"""
	Refresh the login token by executing Django's model save()

	:type user: User
	:param user: The user to have their token refreshed
	"""

	# Trigger an update to the last_login attribute of the user
	user.save()

def isTokenExpired(user):
	"""
	Check if a user's login token has expired.

	:type user: User
	:param user: The user to check for if their token has expired

	:rtype: Boolean
	:returns: True (token has expired) / False (token hasn't expired)
	"""
	now = timezone.now()
	diff = now - user.last_login

	if int(diff.days) >= LOGIN_TOKEN_EXPIRATION:
		return True

	return False

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

def verify_password_with_policy(password):
	"""
	Helper function to validate that the password used during registration meets the password policy.
	Note: If the password violates the policy an exception will be raised.

	:type password: String
	:param password: The password entered by the user
	"""

	# Validate password length
	if len(password) < PASSWORD_POLICY['Min Length']:
		raise Exception("The password does not meet the minimum password length of " + str(PASSWORD_POLICY['Min Length']) + ' characters.')

	if len(password) > PASSWORD_POLICY['Max Length']:
		raise Exception("The password does not meet the maximum password length. Passwords may not exceed " + str(PASSWORD_POLICY['Max Length']) + ' characters.')

	# Validate that there is at least 1 character from each of the listed requirements
	requirements = PASSWORD_POLICY['Requirements']
	for req in requirements:
		req_enabled, req_list = requirements[req]
		if req_enabled:
			contains = any(s in password for s in req_list)
			if not contains:
				raise Exception("The password does not meet the password requirements: needs to contain at least 1 " + str(req).lower() + " character.")

def verify_valid_email(email):
	"""
	Helper function to validate a new user's email address.
	Note: If the email is not valid an exception will be raised.

	:type email: String
	:param email: The email address entered by the user
	"""

	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		raise Exception("The email address provided is not valid, please try again.")

def verify_valid_username(username):
	"""
	Helper function to validate a new user's username.
	Note: If the username is not valid an exception will be raised

	:type username: String
	:param username: The username entered by the user
	"""

	if len(username) > 16:
		raise Exception("The username provided is too long. The maximum number of characters for a username is 16.")

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

	# Validate that the password meets the password policy
	verify_password_with_policy(password)
	
	# Validate that the email is a valid email address
	verify_valid_email(email)

	# Validate that the username is valid
	verify_valid_username(username)

	# Encrypt the password
	encryptPass = encrypt(password)

	# Create the user
	newUser = Users(username=username, password=encryptPass, email=email)
	newUser.save()
	
	# Return the user
	return newUser