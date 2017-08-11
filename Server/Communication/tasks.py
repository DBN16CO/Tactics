import celery
import logging
import datetime
import json
from Server import config
from channels import Channel
from Communication.models import AsyncMessages
from celery.utils.log import get_task_logger
from django.db import transaction
from Server.config import MESSAGE_EXPIRATION
from django.utils import timezone

logger = get_task_logger(__name__)
fh = logging.FileHandler('./{0}'.format(config.MESSAGE_QUEUE_LOG_NAME), mode='a')
logger.addHandler(fh)
logger.setLevel(config.MESSAGE_QUEUE_LOG_LEVEL)

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

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=config.MESSAGE_QUEUE_INTERVAL))
def process_message_queue():
	try:
		with transaction.atomic():
			messages = AsyncMessages.objects.select_for_update()

			for message in messages:
				sent = message.sent
				if not sent:
					channel_name = message.user.channel
					msg = message.message_key
					data = message.data

					msg = {"ID": message.id, "Key": msg, "Data": data}

					# Send message to user
					logging.debug("Sending {} message: {}".format(message.user.username, msg))
					channel = Channel(channel_name)
					channel.send({u'bytes': json.dumps(msg)})

					message.sent = True
					message.save()
					continue

				if message.received:
					logging.debug("Message response received, deleting message")
					message.delete()
				else:
					if is_message_expired(message):
						logger.debug("Message with id {} has expired.".format(message.id))
						# TODO: Send an email once email notifications are implemented

						# Delete the expired message
						message.delete()

	except Exception as e:
		logging.exception(e)