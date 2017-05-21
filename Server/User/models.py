from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Users(models.Model):
	username   = models.CharField(max_length=16, unique=True)
	channel    = models.CharField(max_length=100, default=None, null=True)
	password   = models.CharField(max_length=100)
	email      = models.EmailField(unique=True)
	verified   = models.BooleanField(default=False)
	level      = models.IntegerField(default=1)
	experience = models.IntegerField(default=0)
	coins      = models.IntegerField(default=0)
	created    = models.DateTimeField(auto_now=False, auto_now_add=True)
	last_login = models.DateTimeField(auto_now=True)
	pref_grid  = models.IntegerField(default=100)
	token      = models.CharField(max_length=50, unique=True, default=None, null=True)