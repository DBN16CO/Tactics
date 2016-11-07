from django.test import TestCase
from Communication.testhelper import *
import json

class TestUser(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_create_user(self):
		self.channel.send('{"Command":"CU","username":"testuser1","pw":"12345","email":"a@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))

	def test_duplicate_username(self):
		self.channel.send('{"Command":"CU","username":"testuser1","pw":"12345","email":"a@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
		self.channel.send('{"Command":"CU","username":"testuser1","pw":"12345","email":"b@b.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False, "Error":"That username already exists."}))

	def test_duplicate_email(self):
		self.channel.send('{"Command":"CU","username":"testuser1","pw":"12345","email":"a@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":True}))
		self.channel.send('{"Command":"CU","username":"testuser2","pw":"12345","email":"a@a.com"}')
		result = self.channel.receive()
		self.assertEqual(result, json.dumps({"Success":False, "Error":"That email is already in use."}))