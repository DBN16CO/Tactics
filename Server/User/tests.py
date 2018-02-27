from django.test import TestCase
from Communication.testhelper import *
import json
from User.models import Users
import datetime
import logging
from Server import config
from fcm_django.models import FCMDevice

class TestCreateUser(CommonTestHelper):
	"""
	Tests the following:\n
	- Can successfully create the user (Test 01)\n
	- Cannot create two users with the same:\n
		+ Username (Test 02)\n
		+ Email (Test 03)\n
	- Invalid email returns an error message (Test 04)\n
	- Invalid username returns an error message (Test 05)\n
	- If any of username, email, or password are missing, an error message is returned (Test 06)\n
	- The password rules work as designed (Test 07)
	"""
	def test_cu_01_create_user_success(self):
		result = self.testHelper.createTestUser({"username":"successUsr1","password":self.testHelper.generateValidPassword(),"email":"success@a.com"})
		self.assertTrue(result["Success"])
		self.assertTrue(result["Token"] != None)
		user = Users.objects.get(username="successUsr1")
		self.assertTrue(user.token != None)
		self.assertTrue(user.channel == self.testHelper.channel.name + str(1))

	def test_cu_02_duplicate_username(self):
		# Create user once
		result = self.testHelper.createTestUser({"username":"testDupUser1","password":self.testHelper.generateValidPassword(),"email":"dupUser@a.com"})
		self.assertTrue(result["Success"])

		# Attempt to create user with same username
		result = self.testHelper.createTestUser({"username":"testDupUser1","password":self.testHelper.generateValidPassword(),"email":"dupUser@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That username already exists.")

	def test_cu_03_duplicate_email(self):
		# Create user
		result = self.testHelper.createTestUser({"username":"dupEmailUsr1","password":self.testHelper.generateValidPassword(),"email":"dupEmail@a.com"})
		self.assertTrue(result["Success"])

		# Attempt to create user with same email
		result = self.testHelper.createTestUser({"username":"dupEmailUsr2","password":self.testHelper.generateValidPassword(),"email":"dupEmail@a.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "That email is already in use.")

	def test_cu_04_invalid_email_address(self):
		result = self.testHelper.createTestUser({"username":"invalidEmail","password":self.testHelper.generateValidPassword(),"email":"invalid"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The email address provided is not valid, please try again.")

	def test_cu_05_invalid_username(self):
		result = self.testHelper.createTestUser({"username":"TooLongOfAUsername","password":self.testHelper.generateValidPassword(),"email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The username provided is too long. The maximum number of characters for a username is 16.")

	def test_cu_06_missing_values(self):
		request = {"Command": "CU", "pw":self.testHelper.generateValidPassword(),"email":"t@t.com"}
		self.helper_execute_failure(request, "No username was provided.")

		request = {"Command": "CU", "username":"dupEmailUsr2", "email":"t@t.com"}
		self.helper_execute_failure(request, "No password was provided.")

		request = {"Command": "CU", "username":"dupEmailUsr2", "pw":self.testHelper.generateValidPassword()}
		self.helper_execute_failure(request, "No email address was provided.")

	def test_cu_07_password_policy_failures(self):
		result = self.testHelper.createTestUser({"username":"minPW","password":"asd", "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the minimum password length of " + 
			str(config.PASSWORD_POLICY['Min Length']) + " characters.")
		max_pw = ''
		for _ in range(0, config.PASSWORD_POLICY['Max Length'] + 1):
			max_pw += 'a'

		result = self.testHelper.createTestUser({"username":"maxPW","password":max_pw, "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the maximum password length. Passwords may not exceed " + 
			str(config.PASSWORD_POLICY['Max Length']) + " characters.")
		config.PASSWORD_POLICY['Requirements']['Lowercase'][0] = True
		config.PASSWORD_POLICY['Requirements']['Uppercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Number'][0] = False
		config.PASSWORD_POLICY['Requirements']['Symbol'][0] = False
		result = self.testHelper.createTestUser({"username":"noLower", "password":"ABCDEFG", "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the password requirements: needs to contain at least 1 lowercase character.")

		config.PASSWORD_POLICY['Requirements']['Lowercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Uppercase'][0] = True
		config.PASSWORD_POLICY['Requirements']['Number'][0] = False
		config.PASSWORD_POLICY['Requirements']['Symbol'][0] = False
		result = self.testHelper.createTestUser({"username":"noUpper", "password":"abcdefg", "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the password requirements: needs to contain at least 1 uppercase character.")

		config.PASSWORD_POLICY['Requirements']['Lowercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Uppercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Number'][0] = True
		config.PASSWORD_POLICY['Requirements']['Symbol'][0] = False
		result = self.testHelper.createTestUser({"username":"noNumber", "password":"ABCDEFG", "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the password requirements: needs to contain at least 1 number character.")

		config.PASSWORD_POLICY['Requirements']['Lowercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Uppercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Number'][0] = False
		config.PASSWORD_POLICY['Requirements']['Symbol'][0] = True
		result = self.testHelper.createTestUser({"username":"noSymbol", "password":"ABCDEFG", "email":"t@t.com"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "The password does not meet the password requirements: needs to contain at least 1 symbol character.")

		config.PASSWORD_POLICY['Requirements']['Lowercase'][0] = True
		config.PASSWORD_POLICY['Requirements']['Uppercase'][0] = False
		config.PASSWORD_POLICY['Requirements']['Number'][0] = False
		config.PASSWORD_POLICY['Requirements']['Symbol'][0] = False

class TestLoginLogout(CommonTestHelper):
	"""
	Tests the following cases:\n
	- Can log in successfully with the correct username and password (Test 01)\n
	- Can log in successfully with the correct token (Test 03)\n
	- Logging in with the wrong password returns a failure message (Test 02)\n
	- Logging in with the wrong token returns a failure message (Test 04)\n
	- Can log out successfully (Test 05)\n
	- Logging out without first logging in returns an error message (Test 06)\n
	- Can successfully get all of the user preferences (Test 07)\n
	- Must login again once the login token expires (Test 08)\n
	"""
	def setUp(self):
		super(TestLoginLogout, self).setUp()

		self.credentials = {
			"username" : "loginUser",
			"password" : self.testHelper.generateValidPassword(),
			"email"    : "loginEmail@email.com"
		}
		self.result = self.testHelper.createTestUser(self.credentials)
		self.assertTrue(self.result["Success"])

		self.logout = {"Command":"LGO"}
		self.pa = {"Command":"PA"}

	def test_lo_01_in_success_username_password(self):
		result = self.testHelper.login({"username": self.credentials["username"],
			"password": self.credentials["password"]})
		self.assertTrue(result["Success"])
		self.assertTrue(result["Token"] != None)

		user = Users.objects.get(username=self.credentials["username"])
		self.assertTrue(user.token != None)
		self.assertTrue(user.channel == self.testHelper.channel.name + str(1))

		self.testHelper.send('{"Command": "PA"}')
		result = json.loads(self.testHelper.receive())

		self.assertTrue("PONG_AUTH" in result)

	def test_lo_02_in_failure_username_password(self):
		result = self.testHelper.login({"username":self.credentials["username"],
			"password": "12345"})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "Invalid Username/Password.")

	def test_lo_03_in_success_token(self):
		result = self.testHelper.login({"token": self.result["Token"]})
		self.assertTrue(result["Success"])
		self.assertTrue(Users.objects.get(username=self.credentials["username"]).token != None)

		self.testHelper.send('{"Command": "PA"}')
		result = json.loads(self.testHelper.receive())

		self.assertTrue("PONG_AUTH" in result)

	def test_lo_04_in_failure_token(self):
		result = self.testHelper.login({"token": "asdljkfahsdjfkl23874ajkshdf"})
		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "Invalid Username/Password.")

	def test_lo_05_out_success(self):
		result = self.testHelper.login({"username": self.credentials["username"],
			"password": self.credentials["password"]})

		self.helper_execute_success(self.logout)

		user = Users.objects.get(username=self.credentials["username"])
		self.assertTrue(user.token == None)
		self.assertTrue(user.channel == None)

		self.helper_execute_failure(self.pa, "User is not authenticated, please login.")

	def test_lo_06_out_failure(self):
		self.helper_execute_success(self.logout)
		self.helper_execute_failure(self.logout, "User is not authenticated, please login.")

	def test_lo_07_get_user_info_success(self):
		result = self.testHelper.login({"username": self.credentials["username"],
			"password": self.credentials["password"]})

		user = Users.objects.get(username=self.credentials["username"])

		self.assertTrue(user.token != None)

		self.testHelper.send('{"Command": "GUI"}')
		result = json.loads(self.testHelper.receive())

		self.assertTrue(result["Success"])
		self.assertEquals(result["Username"], user.username)
		self.assertEquals(result["Email"], user.email)
		self.assertEquals(result["Verified"], user.verified)
		self.assertEquals(result["Level"], user.level)
		self.assertEquals(result["Experience"], user.experience)
		self.assertEquals(result["Coins"], user.coins)
		self.assertEquals(result["Preferences"], user.prefs)

	def test_lo_08_login_token_expire(self):
		user = Users.objects.filter(username=self.credentials["username"])

		self.assertTrue(user.first().token != None)

		update_login = user.first().last_login - datetime.timedelta(days=15)
		user.update(last_login=update_login)

		result = self.testHelper.login({"token": self.result["Token"]})
		self.assertFalse(result["Success"])
		self.assertEquals(result["Error"], "Login token has expired, please login again using your username/password.")

	def test_lo_08_send_user_info_success(self):
		result = self.testHelper.login({"username": self.credentials["username"],
			"password": self.credentials["password"]})

		reg_id = 'abc123'

		cmd = {
			"Command": "SUI",
			"Notifications": {
				"RegistrationID": reg_id,
				"DeviceType": "android"
			},
			"Preferences": {
				"Grid Opacity": 99
			}
		}

		self.testHelper.send(json.dumps(cmd))
		result = json.loads(self.testHelper.receive())

		self.assertTrue(result['Success'])

		user = Users.objects.get(username=self.credentials["username"])

		self.assertEquals(user.prefs['Grid Opacity'], 99)

		device = user.device
		self.assertEquals(device.type, 'android')
		self.assertEquals(device.registration_id, reg_id)

	def test_lo_09_send_user_info_invalid_data(self):
		result = self.testHelper.login({"username": self.credentials["username"],
			"password": self.credentials["password"]})

		reg_id = None

		cmd = {
			"Command": "SUI",
			"Notifications": {
				"RegistrationID": reg_id,
				"DeviceType": "android"
			},
			"Preferences": {
				"Grid Opacity": 99
			}
		}

		self.helper_execute_failure(cmd, "Notification Registration ID is missing for GCM Settings")

		cmd["Notifications"]["RegistrationID"] = "abc123"
		cmd["Notifications"]["DeviceType"] = None

		self.helper_execute_failure(cmd, "Notification Device type is missing for GCM Settings")

		cmd["Notifications"]["DeviceType"] = "invalid-device"

		self.helper_execute_failure(cmd, "Device type 'invalid-device' is not supported for notifications")

		cmd["Notifications"]["DeviceType"] = 'ios'
		cmd["Preferences"]["invalid-pref"] = "data"

		self.helper_execute_failure(cmd, "User preference 'invalid-pref' is not a known preference.")


