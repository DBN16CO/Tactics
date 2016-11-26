from django.test import TestCase
from Communication.testhelper import *
from Static.create_data import *
import json

class TestStatic(TestCase):
	def setUp(self):
		self.channel = TestHelper()

	def test1_bad_db_setup(self):
		result = setup_static_db("bad version")
		self.assertFalse(result)

	def test2_initial_load_v1_0(self):
		startTestLog("test_initial_load_v1_0")
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"init_user","password":"abc12345","email":"initUser@email.com"}))

		self.channel.send('{"Command":"IL"}')
		result = self.channel.receive()
		logging.debug(result)

		expected_data = ver_1_0_static_data()

		self.maxDiff = None

		data = json.loads(result)
		expected_data = json.loads(json.dumps(expected_data))
		logging.debug(data)

		self.assertEqual(data["Version"], expected_data["Version"])
		self.assertEqual(data["Actions"], expected_data["Actions"])
		self.assertEqual(data["Classes"], expected_data["Classes"])

		# Ensure the keys match and their values are not null
		self.assertEqual(sorted(data["Leaders"]), sorted(expected_data["Leaders"]))
		for key in data["Leaders"].keys():
			self.assertTrue(data["Leaders"][key] != None)
		self.assertEqual(sorted(data["Maps"]), sorted(expected_data["Maps"]))
		for key in data["Maps"].keys():
			self.assertTrue(data["Maps"][key] != None)
		self.assertEqual(data["Perks"], expected_data["Perks"])
		self.assertEqual(data["Stats"], expected_data["Stats"])
		self.assertEqual(sorted(data["Terrain"]), sorted(expected_data["Terrain"]))
		for key in data["Terrain"].keys():
			self.assertTrue(data["Terrain"][key] != None)
			for clss in data["Terrain"][key]["Units"].keys():
				self.assertTrue(data["Terrain"][key]["Units"][clss] != None)

		# Verify the success
		self.assertEqual(data["Success"], True)

		endTestLog("test_initial_load_v1_0")

	def test3_bad_version(self):
		startTestLog("test_initial_load_v1_0")
		self.assertTrue(self.channel.createUserAndLogin(
			{"username":"init_user","password":"abc12345","email":"initUser@email.com"}))

		bad_ver = Version(name="bad version")
		bad_ver.save()

		self.channel.send('{"Command":"IL"}')
		result = self.channel.receive()
		logging.debug(result)

		self.assertEqual(result, json.dumps({"Success": False, "Error": "The following tables could not be loaded: Actions, Classes, Leaders, Maps, Perks, Stats, Terrain"}))
