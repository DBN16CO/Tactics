from django.test import TestCase
from Communication.testhelper import *
import json

class TestUser(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test1_create_user(self):
		logging.debug("==== Starting create user test ====")

		result = self.channel.createTestUser({"username":"successUsr1","password":"12345","email":"success@a.com"})
		self.assertTrue(result["Success"])

		logging.debug("==== Exiting create user test ====")

	def test2_duplicate_username(self):
		logging.debug("==== Starting duplicate user test ====")

		result = self.channel.createTestUser({"username":"testDupUser1","password":"12345","email":"dupUser@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.createTestUser({"username":"testDupUser1","password":"12345","email":"dupUser@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That username already exists.")

		logging.debug("==== Exiting duplicate user test ====")

	def test3_duplicate_email(self):
		logging.debug("==== Starting duplicate email test ====")

		result = self.channel.createTestUser({"username":"dupEmailUsr1","password":"12345","email":"dupEmail@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.createTestUser({"username":"dupEmailUsr2","password":"12345","email":"dupEmail@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That email is already in use.")

		logging.debug("==== Exiting duplicate email test ====")

	def test4_login_success_username_password(self):
		logging.debug("==== Starting login success username/password test ====")

		result = self.channel.createTestUser({"username":"testLoginSuccess","password":"12345","email":"loginSuccess@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"username": "testLoginSuccess", "password": "12345"})
		self.assertTrue(result["Success"])
		self.assertTrue(result["Token"] != None)

		self.channel.send('{"Command": "PA"}')
		result = json.loads(self.channel.receive())

		self.assertTrue("PONG_AUTH" in result)

		logging.debug("==== Exiting login success username/password test ====")

	def test5_login_failure_username_password(self):
		logging.debug("==== Starting login failure username/password test ====")

		result = self.channel.createTestUser({"username":"testLoginFailure","password":"12345","email":"loginFailure@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"username": "testLoginFailure", "password": "asdfasdfa"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "Invalid Username/Password")

		logging.debug("==== Exiting login failure username/password test ====")

	def test6_login_success_token(self):
		logging.debug("==== Starting login success token test ====")

		result = self.channel.createTestUser({"username": "testLoginSToken", "password": "12345", "email": "loginSuccessToken@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"token": result["Token"]})
		self.assertTrue(result["Success"])

		self.channel.send('{"Command": "PA"}')
		result = json.loads(self.channel.receive())

		self.assertTrue("PONG_AUTH" in result)

		logging.debug("==== Exiting login success token test ====")

	def test7_login_failure_token(self):
		logging.debug("==== Starting login failure token test ====")

		result = self.channel.createTestUser({"username": "testLoginFToken", "password": "12345", "email": "loginSuccessToken@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"token": "asdljkfahsdjfkl23874ajkshdf"})
		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "Invalid Username/Password")

		logging.debug("==== Exiting login failure token test ====")



# TODO
#	Test missing of each value needed for creating a user
#   Test missing of each value needed for logging in
#   Test invalid passwords (once we come up with password rules)
#   Test invalid username/email etc (username too long or too short or invalid email)