from django.test import TestCase
from Communication.testhelper import *
import json
from User.models import Users

class TestUser(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test1_create_user_success(self):
		startTestLog("test1_create_user_success")

		result = self.channel.createTestUser({"username":"successUsr1","password":"12345","email":"success@a.com"})
		self.assertTrue(result["Success"])
		self.assertTrue(result["Token"] != None)
		self.assertTrue(Users.objects.get(username="successUsr1").token != None)

		endTestLog("test1_create_user_success")

	def test2_duplicate_username(self):
		startTestLog("test2_duplicate_username")

		result = self.channel.createTestUser({"username":"testDupUser1","password":"12345","email":"dupUser@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.createTestUser({"username":"testDupUser1","password":"12345","email":"dupUser@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That username already exists.")

		endTestLog("test2_duplicate_username")

	def test3_duplicate_email(self):
		startTestLog("test3_duplicate_email")

		result = self.channel.createTestUser({"username":"dupEmailUsr1","password":"12345","email":"dupEmail@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.createTestUser({"username":"dupEmailUsr2","password":"12345","email":"dupEmail@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That email is already in use.")

		endTestLog("test3_duplicate_email")

	def test4_login_success_username_password(self):
		startTestLog("test4_login_success_username_password")

		result = self.channel.createTestUser({"username":"testLoginSuccess","password":"12345","email":"loginSuccess@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"username": "testLoginSuccess", "password": "12345"})
		self.assertTrue(result["Success"])
		self.assertTrue(result["Token"] != None)
		self.assertTrue(Users.objects.get(username="testLoginSuccess").token != None)

		self.channel.send('{"Command": "PA"}')
		result = json.loads(self.channel.receive())

		self.assertTrue("PONG_AUTH" in result)

		endTestLog("test4_login_success_username_password")

	def test5_login_failure_username_password(self):
		startTestLog("test5_login_failure_username_password")

		result = self.channel.createTestUser({"username":"testLoginFailure","password":"12345","email":"loginFailure@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"username": "testLoginFailure", "password": "asdfasdfa"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "Invalid Username/Password.")

		endTestLog("test5_login_failure_username_password")

	def test6_login_success_token(self):
		startTestLog("test6_login_success_token")

		result = self.channel.createTestUser({"username": "testLoginSToken", "password": "12345", "email": "loginSuccessToken@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"token": result["Token"]})
		self.assertTrue(result["Success"])
		self.assertTrue(Users.objects.get(username="testLoginSToken").token != None)

		self.channel.send('{"Command": "PA"}')
		result = json.loads(self.channel.receive())

		self.assertTrue("PONG_AUTH" in result)

		endTestLog("test6_login_success_token")

	def test7_login_failure_token(self):
		startTestLog("test7_login_failure_token")

		result = self.channel.createTestUser({"username": "testLoginFToken", "password": "12345", "email": "loginSuccessToken@a.com"})
		self.assertTrue(result["Success"])

		result = self.channel.login({"token": "asdljkfahsdjfkl23874ajkshdf"})
		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "Invalid Username/Password.")

		endTestLog("test7_login_failure_token")

	def test8_logout_success(self):
		startTestLog("test8_logout_success")

		self.assertTrue(self.channel.createUserAndLogin({"username": "testLogoutS", "password": "12345", "email": "logoutSuccess@a.com"}))
		self.assertTrue(Users.objects.get(username="testLogoutS").token != None)


		self.channel.send('{"Command": "LGO"}')
		result = json.loads(self.channel.receive())
		self.assertTrue(result["Success"])

		self.assertTrue(Users.objects.get(username="testLogoutS").token == None)

		self.channel.send('{"Command": "PA"}')
		result = json.loads(self.channel.receive())

		self.assertTrue("Success" in result)
		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "User is not authenticated, please login.")

		endTestLog("test8_logout_success")

	def test9_logout_failure(self):
		startTestLog("test9_logout_failure")

		self.channel.send('{"Command": "LGO"}')
		result = json.loads(self.channel.receive())
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "User is not authenticated, please login.")

		endTestLog("test9_logout_failure")

	def test10_get_user_info_success(self):
		startTestLog("test10_get_user_info_success")

		self.assertTrue(self.channel.createUserAndLogin({"username": "testGUI", "password": "12345", "email": "testGUI@a.com"}))

		user = Users.objects.get(username="testGUI")

		self.assertTrue(user.token != None)

		self.channel.send('{"Command": "GUI"}')
		result = json.loads(self.channel.receive())

		self.assertTrue(result["Success"])
		self.assertEquals(result["Username"], user.username)
		self.assertEquals(result["Email"], user.email)
		self.assertEquals(result["Verified"], user.verified)
		self.assertEquals(result["Level"], user.level)
		self.assertEquals(result["Experience"], user.experience)
		self.assertEquals(result["Coins"], user.coins)
		self.assertEquals(result["Preferences"]["Grid Opacity"], user.pref_grid)

		endTestLog("test10_get_user_info_success")


# TODO
#	Test missing of each value needed for creating a user
#   Test missing of each value needed for logging in
#   Test invalid passwords (once we come up with password rules)
#   Test invalid username/email etc (username too long or too short or invalid email)