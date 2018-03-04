from testhelper import *
from router import *
import json
from Game.tests import TestGame
from Game.models import Game
from Game import maphelper
from Static.models import Version
from tasks import process_message_queue
from models import AsyncMessages
from fcm_django.models import FCMDevice
from User.models import Users

class TestCommunication(CommonTestHelper):
	"""
	Tests the following:
	- Pinging the server returns pong (Test 01)\n
	- Sending in a fake command returns an error message (Test 02)\n
	- Sending in a request with no command returns a message (Test 03)
	- Sending a command with invlid JSON will return an error message (Test 04)\n
	- Sending a command without being authenticated will return an error message (Test 05)\n
	- When the map data is empty for a version it is reloaded successfully (Test 06)\n
	"""
	def test_cm_01_ping_server(self):
		self.testHelper.send('{"PING":"PING"}')
		result = self.testHelper.receive()
		self.assertEqual(result, json.dumps({"PONG":"PONG"}))

	def test_cm_02_internal_error(self):
		# Create user and login
		self.assertTrue(self.testHelper.createUserAndLogin(
			{"username":"bad_cmd_usr","password":self.testHelper.generateValidPassword(),"email":"bcu@email.com"}))

		cmd = {"Command":"fake_command"}
		self.helper_execute_failure(cmd, "Invalid command.")

	def test_cm_03_missing_command(self):
		self.helper_execute_failure({}, "The command information is incomplete.")

	def test_cm_04_invalid_json(self):
		self.testHelper.send({}, 1)
		result = json.loads(self.testHelper.receive(1))

		self.assertFalse(result["Success"])
		self.assertEqual(result["Error"], "Input JSON invalid.")

	def test_cm_05_unauthenthicated_access(self):
		self.helper_execute_failure({"Command":"AAA"}, "User is not authenticated, please login.")

	def test_cm_06_reload_static_maps(self):
		maphelper.maps = {}

		self.assertTrue(self.testHelper.createUserAndLogin(
			{"username":"bad_cmd_usr","password":self.testHelper.generateValidPassword(),"email":"bcu@email.com"}))

		# Run a command that reloads the map object
		self.helper_execute_failure({"Command":"TA"}, "Internal Error: Game Key missing.")

		version = Version.objects.latest('pk')

		# Ensure that the map object was reloaded
		self.assertTrue(version.name in maphelper.maps)

class TestReceivedMessage(TestGame):
	"""
	Tests the following:
	- Test Sending Async Messages to matched users and sending valid RM commands back\n
	- Test Sending Async Messages to matched users and sending an invalid RM commands back\n
	"""
	def setUp(self):
		super(TestReceivedMessage, self).setUp()

		self.get_both_users_in_queue()

	def match_players_get_async_messages(self):
		processMatchmakingQueue()
		process_message_queue()

		async_messages = AsyncMessages.objects
		self.assertTrue(async_messages.count() == 2)

		for async_message in async_messages.filter():
			self.assertTrue(async_message.websocket_sent)
			self.assertEquals(async_message.device_title, "Game on!")
			self.assertEquals(async_message.device_message, "A match has been found!")
			self.assertEquals(async_message.device_sound, "default")
			self.assertEquals(async_message.device_icon, None)

		async_first = self.testHelper.receive()
		async_second = self.testHelper.receive(2)

		async_first = json.loads(async_first)
		async_second = json.loads(async_second)

		return async_first, async_second

	def verify_basic_data_response(self, async_first, async_second):
		game = Game.objects.filter().first()

		expected_first = {"Key": "MATCH_FOUND", "Data": {"Game_ID": game.id}}
		expected_second = {"Key": "MATCH_FOUND", "Data": {"Game_ID": game.id}}

		self.assertDictContainsSubset(expected_first, async_first,
			"Received: {} Expected: {}".format(async_first, expected_first))
		self.assertDictContainsSubset(expected_second, async_second,
			"Received: {} Expected: {}".format(async_second, expected_second))

	def test_rm_01_received_message_success(self):
		async_messages = AsyncMessages.objects
		async_first, async_second = self.match_players_get_async_messages()

		self.verify_basic_data_response(async_first, async_second)

		self.testHelper.send(json.dumps({"Command": "RM", "message_id": async_first['ID']}))
		success = json.loads(self.testHelper.receive())
		self.assertTrue({"Success": True} == success, "RM Response: {}".format(success))

		self.testHelper.send(json.dumps({"Command": "RM", "message_id": async_second['ID']}), 2)
		success = json.loads(self.testHelper.receive(2))
		self.assertTrue({"Success": True} == success, "RM Response: {}".format(success))

		self.assertTrue(async_messages.count() == 2, "Async Message Count: {}".format(async_messages.count()))
		for async_message in async_messages.filter():
			self.assertTrue(async_message.received)

		process_message_queue()
		self.assertTrue(async_messages.count() == 0, "Async Message Count: {}".format(async_messages.count()))

	def test_rm_02_received_message_incorrect_message_id(self):
		async_messages = AsyncMessages.objects
		async_first, async_second = self.match_players_get_async_messages()

		self.verify_basic_data_response(async_first, async_second)

		self.testHelper.send(json.dumps({"Command": "RM", "message_id": -1}))
		success = json.loads(self.testHelper.receive())
		self.assertTrue({"Success": False, "Error": "Could not find the server message to mark as received."} == success, "RM Response: {}".format(success))

		self.testHelper.send(json.dumps({"Command": "RM", "message_id": -1}), 2)
		success = json.loads(self.testHelper.receive(2))
		self.assertTrue({"Success": False, "Error": "Could not find the server message to mark as received."} == success, "RM Response: {}".format(success))

		self.assertTrue(async_messages.count() == 2, "Async Message Count: {}".format(async_messages.count()))
		for async_message in async_messages.filter():
			self.assertFalse(async_message.received)

		process_message_queue()
		self.assertTrue(async_messages.count() == 2, "Async Message Count: {}".format(async_messages.count()))

	def test_rm_03_async_message_expiration_notify(self):
		async_messages = AsyncMessages.objects
		self.match_players_get_async_messages()

		# Create fake user devices for testing the notification path
		i = 0
		for user in Users.objects.filter():
			device = FCMDevice(registration_id="reg%d" % i, type="android", active=True)
			device.save()

			user.device = device
			user.save()

			i += 1

		for async_message in async_messages.filter():
			message_updated = async_message.updated - datetime.timedelta(seconds=1900)
			async_message_query = async_messages.filter(pk=async_message.id)
			async_message_query.update(updated=message_updated)

		self.assertTrue(async_messages.count() == 2, "Async Message Count: {}".format(async_messages.count()))
		process_message_queue(notify_expected=True)
		self.assertTrue(async_messages.count() == 0, "Async Message Count: {}".format(async_messages.count()))

	def test_rm_04_async_message_expiration_no_notify(self):
		async_messages = AsyncMessages.objects
		self.match_players_get_async_messages()

		# Create fake user devices for testing the notification path
		i = 0
		for user in Users.objects.filter():
			device = FCMDevice(registration_id="reg%d" % i, type="android", active=True)
			device.save()

			user.device = device
			user.save()

			i += 1

		for async_message in async_messages.filter():
			message_updated = async_message.updated - datetime.timedelta(seconds=1900)
			async_message_query = async_messages.filter(pk=async_message.id)
			async_message_query.update(updated=message_updated, device_title=None)

		self.assertTrue(async_messages.count() == 2, "Async Message Count: {}".format(async_messages.count()))
		process_message_queue(notify_expected=False)
		self.assertTrue(async_messages.count() == 0, "Async Message Count: {}".format(async_messages.count()))