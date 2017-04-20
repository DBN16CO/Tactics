from __future__ import unicode_literals

from django.db import models

class AdminUsers(models.Model):
	username   = models.CharField(max_length=16, unique=True)
	password   = models.CharField(max_length=100)

class ServerStats(models.Model):
	name         = models.CharField(max_length=25, null=True, default=None)
	value        = models.TextField()