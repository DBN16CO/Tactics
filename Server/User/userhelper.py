#from ..Static.models import Class, Stat, Version
from User.models import Users

""" 
This file is used to store all methods helping with the processing of user objects
"""

# Creates a user with the provided values
def createUser(username, password, email):
	#TODO Create validation for user values
	
	#TODO encrypt the password
	encryptPass = password

	# Create the user
	newUser = Users(username=username, password=encryptPass, email=email)
	newUser.save()

	#TODO Logic for verifying email
	
	# Return the user
	return newUser