from django.test import TestCase
from Communication.testhelper import *
import json

class TestCommunication(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test_create_unit(self):
		return