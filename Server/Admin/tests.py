import os
from django.test import Client
from models import AdminUsers
from Communication.testhelper import *
from User.models import Users
from User.userhelper import encrypt

class TestAdmin(CommonTestHelper):

	def _create_admin_account(self, username, password):
		user = AdminUsers(username=username, password=encrypt(password))
		user.save()

	def _login(self):
		# follow = True will cause the web client to follow all redirects - in this case redirects to the main console
		response = self.client.post('/admin/', {"form-type": "login", "username": self.admin_user, "password": self.admin_pass}, follow=True)
		self.assertTrue(response.status_code == 200)
		self.assertTrue('/admin?logout=true' in response.content)

		return response

	def setUp(self):
		self.client = Client()
		self.admin_user = 'test'
		self.admin_pass = 'testpass'
		self._create_admin_account(self.admin_user, self.admin_pass)

	def test_ADMIN_01_failed_login(self):
		response = self.client.get('/admin/')
		self.assertTrue(response.status_code == 200)
		self.assertTrue('admin-login' in response.content)

		# follow = True will cause the web client to follow all redirects - in this case redirects back to login page
		response = self.client.post('/admin/', {"form-type": "login", "username": "invalid", "password": "invalid"}, follow=True)
		self.assertTrue(response.status_code == 200)
		self.assertTrue('admin-login' in response.content)

	def test_ADMIN_02_successful_login(self):
		self._login()

	def test_ADMIN_03_successful_logout(self):
		self._login()

		response = self.client.get('/admin?logout=true', follow=True)
		self.assertTrue(response.status_code == 200)
		self.assertTrue('admin-login' in response.content)

	def test_ADMIN_04_basic_performance_page(self):
		# Setup a game web socket connection for this test
		super(TestAdmin, self).setUp()

		response = self._login()

		# This will exist when no performance stats exist
		self.assertTrue('&lt;No Requests&gt;' in response.content)

		# Temporarily allow performance stats to be archived
		os.environ.pop('TEST_ENV')
		self.testHelper.createUserAndLogin({"username": "test", "password": "test1234", "email": "t@t.com"})
		os.environ['TEST_ENV'] = "TEST_ENV"

		# Validate that the performance data is visible on the admin page
		response = self.client.get('/admin/')
		self.assertFalse('&lt;No Requests&gt;' in response.content)
		self.assertTrue('LGN' in response.content)
		self.assertTrue('CU' in response.content)

	def test_ADMIN_05_basic_user_page(self):
		# Setup a game web socket connection for this test
		super(TestAdmin, self).setUp()

		response = self._login()

		self.testHelper.createTestUser({"username": "test", "password": "test1234", "email": "t@t.com"})
		
		response = self.client.get('/admin/')

		total_users = """
					<div class="well" style="padding: 3px;">
							<h5 align="center">Total Registered Users</h5>
							<h3 align="center">1</h3>
					</div>
					"""
		total_users = total_users.replace(" ", "").replace("\t", "")
		stripped_response = response.content.replace(" ", "").replace("\t", "")
		self.assertTrue(total_users in stripped_response)

		new_users = """
					<div class="well" style="padding: 3px;">
						<h5 align="center">New Registered Users (past 24 hrs)</h5>
						<h3 align="center">1</h3>
					</div>
					"""
		new_users = new_users.replace(" ", "").replace("\t", "")
		self.assertTrue(new_users in stripped_response)

	def test_ADMIN_06_basic_edit_user(self):
		# Setup a game web socket connection for this test
		super(TestAdmin, self).setUp()

		response = self._login()

		self.testHelper.createTestUser({"username": "test", "password": "test1234", "email": "t@t.com"})
		
		response = self.client.get('/admin/')

		self.assertTrue('test' in response.content)
		self.assertTrue('t@t.com' in response.content)

		user = Users.objects.filter()[0]
		user_id = user.id

		response = self.client.post('/admin/', {"form-type": "edit-user", "user_id": user_id, "username": "test1", "email": "tt@tt.com", "level": 2, "experience": 2}, follow=True)
		self.assertTrue('test1' in response.content)
		self.assertTrue('tt@tt.com' in response.content)

		user = Users.objects.filter()[0]
		self.assertTrue(user.username == 'test1')
		self.assertTrue(user.email == 'tt@tt.com')
		self.assertTrue(user.level == 2)
		self.assertTrue(user.experience == 2)

