from __future__ import unicode_literals

from django.db import models

class AsyncMessages(models.Model):
	created   = models.DateTimeField(auto_now_add=True)
	updated   = models.DateTimeField(auto_now=True)
	user      = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	message   = models.TextField()
	sent      = models.BooleanField(default=False)
	receieved = models.BooleanField(default=False)
