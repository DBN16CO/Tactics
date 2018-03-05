from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models

class AsyncMessages(models.Model):
	created          = models.DateTimeField(auto_now_add=True)
	updated          = models.DateTimeField(auto_now=True)
	user             = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	message_key      = models.TextField()
	device_title     = models.TextField(default=None, null=True)
	device_message   = models.TextField(default=None, null=True)
	device_sound     = models.TextField(default="default")
	device_icon      = models.TextField(default=None, null=True)
	data             = JSONField()
	websocket_sent   = models.BooleanField(default=False)
	received         = models.BooleanField(default=False)
