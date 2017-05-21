import os
import celery
import logging
import datetime
from Server import config
from channels import Channel
from Communication.models import AsyncMessages
from celery.utils.log import get_task_logger
from django.db import transaction

logger = get_task_logger(__name__)
fh = logging.FileHandler('./{0}'.format(config.MESSAGE_QUEUE_LOG_NAME), mode='a')
logger.addHandler(fh)
logger.setLevel(config.MESSAGE_QUEUE_LOG_LEVEL)

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
					channel.send({u'text': msg, u'bytes': msg, u'reply_channel': channel.name})

					message.sent = True
					message.save()
					continue

				if message.received:
					logging.debug("Message response received, deleting message")
					message.delete()
				else:
					updated = message.updated
					if updated:
						# Send email to user
						message.delete()


	except Exception as e:
		logging.exception(e)