import os
import celery
import logging
import datetime
from Server import config
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
fh = logging.FileHandler('./{0}'.format(config.MESSAGE_QUEUE_LOG_NAME), mode='a')
logger.addHandler(fh)
logger.setLevel(config.MESSAGE_QUEUE_LOG_LEVEL)

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=config.MESSAGE_QUEUE_INTERVAL))
def process_message_queue():
	pass