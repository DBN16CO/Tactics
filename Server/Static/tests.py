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

		# Version Check - do the dictionaries match?
		self.assertEqual(data["Version"], expected_data["Version"])

		# Action Check - do the dictionaries match?
		self.assertEqual(data["Actions"], expected_data["Actions"])

		# Class Check - do the dictionaries match?
		self.assertEqual(data["Classes"], expected_data["Classes"])

		# Hero Ability Check - do the dictionaries match?
		self.assertEqual(data["Hero_Abils"], expected_data["Hero_Abils"])

		# Leader Check - Ensure leader keys match, their values are not null, and ability lists, sorted, match
		self.assertEqual(data["Leaders"], expected_data["Leaders"])

		# Map Check - Ensure that each map name exists as a key, and its data is not null
		self.assertEqual(sorted(data["Maps"]), sorted(expected_data["Maps"]))
		for key in data["Maps"].keys():
			self.assertTrue(data["Maps"][key] != None)

			# Test that the map data matches what is saved in the file
			split_map = data["Maps"][key].split("n")
			with open(expected_data["Map_Base"] + expected_data["Maps"][key]) as file:
				counter = 0
				for line in file:
					self.assertTrue(split_map[counter] == line.strip())
					counter += 1

		# Perk Check - do the dictionaries match?
		self.assertEqual(data["Perks"], expected_data["Perks"])

		# Stat Check - do the dictionaries match?
		self.assertEqual(data["Stats"], expected_data["Stats"])

		# Terrain Check - do the dictionaries match?
		self.assertEqual(data["Terrain"], expected_data["Terrain"])

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

		self.assertEqual(result, json.dumps({"Success": False, "Error": "The following tables could not be loaded: Actions, Classes, Hero_Abils, Leaders, Maps, Perks, Stats, Terrain"}))
