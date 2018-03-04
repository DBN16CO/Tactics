import celery
import logging
import datetime
import json
import os
from Server import config
from channels import Channel
from Communication.models import AsyncMessages
from celery.utils.log import get_task_LOGGER
from django.db import transaction
from Server.config import MESSAGE_EXPIRATION
from django.utils import timezone

LOGGER = get_task_LOGGER(__name__)
FHANDLER = logging.FileHandler('./{0}'.format(config.MESSAGE_QUEUE_LOG_NAME), mode='a')
LOGGER.addHandler(FHANDLER)
LOGGER.setLevel(config.MESSAGE_QUEUE_LOG_LEVEL)

def is_message_expired(message):
	"""
	Check if an async message has expired

	:type message: AsyncMessages
	:param message: The async message to check if it has expired

	:rtype: Boolean
	:returns: True (message has expired) / False (message hasn't expired)
	"""
	now = timezone.now()
	diff = now - message.updated

	if int(diff.seconds) >= MESSAGE_EXPIRATION:
		return True

	return False

def send_notification(device, message):
	"""
	Sends the given device a notification.

	:type device: FCMDevice
	:param message: The model of the user's phone

	:type messsage: AsyncMessage
	:param message: Contains the data about the notification settings
	"""
	LOGGER.debug("Sending the user a notification!")
	notify_data = {
		"title": message.device_title,
		"body": message.device_message,
		"sound": message.device_sound
	}

	if message.device_icon:
		notify_data["icon"] = message.device_icon

	result = device.send_message(**notify_data)
	if result['success'] == 1:
		LOGGER.debug("Notification sent successfully!")
	else:
		LOGGER.debug("Notification failed to be sent!")

def send_websocket_message(message):
	"""
	Sends the user's device a message via websocket.

	:type messsage: AsyncMessage
	:param message: Contains the data about the websocket message settings
	"""
	LOGGER.debug("Sending the user a websocket message!")
	channel_name = message.user.channel
	msg = message.message_key
	data = message.data

	msg = {"ID": message.id, "Key": msg, "Data": data}

	# Send message to user
	logging.debug("Sending {} message: {}".format(message.user.username, msg))
	channel = Channel(channel_name)
	channel.send({u'bytes': json.dumps(msg)})

	message.websocket_sent = True
	message.save()

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=config.MESSAGE_QUEUE_INTERVAL))
def process_message_queue(notify_expected=False):
	"""
	Processes the asynchronous message queue.
	Can send messages via websocket or via Google's notification service (Firebase).

	:type notify_expected: bool
	:param notify_expected: Used for indicating if automated tests expect notifications to be sent
	"""
	try:
		with transaction.atomic():
			messages = AsyncMessages.objects.select_for_update()

			for message in messages:
				# Used for automated testing of notification path
				notified = False

				websocket_sent = message.websocket_sent
				if not websocket_sent:
					send_websocket_message(message)
					continue

				if message.received:
					logging.debug("Message response received, deleting message")
					message.delete()
				elif is_message_expired(message):
					LOGGER.debug("Message with id {} has expired.".format(message.id))

					device = message.user.device

					# Only send the user a notification if they have a registered & active device
					is_active_device = device is not None and device.active

					# Only send the user a notification if the message is a message
					# that we want to send notifications for
					is_notify_message = message.device_title != None

					if is_active_device and is_notify_message:
						try:
							send_notification(device, message)
						except Exception:
							if 'TEST_ENV' not in os.environ:
								raise

						# Used for automated testing of notification path
						notified = True

					# Delete the expired message
					message.delete()

				if notify_expected:
					assert notified

	except Exception as exc:
		logging.exception(exc)