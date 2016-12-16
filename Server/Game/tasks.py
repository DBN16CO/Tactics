from __future__ import absolute_import

from celery import shared_task
import celery
import datetime

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=5))
def processMatchmakingQueue():
    return 'The test task executed with argument'