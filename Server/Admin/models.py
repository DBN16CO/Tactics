from __future__ import unicode_literals

from django.db import models

class ServerStats(models.Model):
	name         = models.CharField(max_length=25, null=True, default=None)
	value        = models.TextField()