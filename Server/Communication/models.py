from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models

class AsyncMessages(models.Model):
	created       = models.DateTimeField(auto_now_add=True)
	updated       = models.DateTimeField(auto_now=True)
	user          = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	message_key   = models.TextField()
	data          = JSONField()
	sent          = models.BooleanField(default=False)
	received      = models.BooleanField(default=False)
