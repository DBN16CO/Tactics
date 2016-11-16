from django.test import TestCase
from Communication.testhelper import *
import json

class TestUser(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_create_user(self):
		logging.debug("Starting create user test.")
		self.channel.send('{"Command":"CU","username":"successUsr1","pw":"12345","email":"success@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True, "UserID": 1}))
		logging.debug("Exiting create user test.\n")

	def test_duplicate_username(self):
		logging.debug("Starting duplicate user test.")
		self.channel.send('{"Command":"CU","username":"testDupUser1","pw":"12345","email":"dupUser@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
		self.channel.send('{"Command":"CU","username":"testDupUser1","pw":"12345","email":"dupUser@b.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False, "Error":"That username already exists."}))
		logging.debug("Exiting duplicate user test.\n")

	def test_duplicate_email(self):
		logging.debug("Starting duplicate email test.")
		self.channel.send('{"Command":"CU","username":"dupEmailUsr1","pw":"12345","email":"dupEmail@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
		self.channel.send('{"Command":"CU","username":"dupEmailUsr2","pw":"12345","email":"dupEmail@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False, "Error":"That email is already in use."}))
		logging.debug("Exiting duplicat email test.\n")

	def test_login_success(self):
		logging.debug("Starting login success test.")
		self.channel.send('{"Command":"CU","username":"successUsr1","pw":"12345","email":"success@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True, "UserID": 1}))
		self.channel.send('{"Command":"LGN","username":"successUsr1","pw":"12345"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True, "UserID": 1}))
		logging.debug("Exiting login success test.")

	def test_login_failure(self):
		logging.debug("Starting login failure test.")
		self.channel.send('{"Command":"CU","username":"successUsr1","pw":"12345","email":"success@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True, "UserID": 1}))
		self.channel.send('{"Command":"LGN","username":"successUsr1","pw":"123456"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False, "Error": "Invalid Username/Password"}))
		logging.debug("Exiting login success test.")




# TODO Necessary?
#	def test_missing_username(self):
#		logging.debug("Starting missing username test.")
#		self.channel.send('{"Command":"CU","pw":"12345","email":"nousername@a.com"}')
#		result = self.channel.receive()
#		self.assertEqual(result, json.dumps({"Success":True}))
#		logging.debug("Exiting missing username test.\n")

#	def test_invalid_email(self):
#		self.channel.send('{"Command":"CU","username":"invalEmailUsr","pw":"12345","email":"aaa"}')
#		result = self.channel.receive()
#		self.assertEqual(result, json.dumps({"Success":False, "Error":"That email is already in use."}))