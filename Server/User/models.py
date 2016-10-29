from __future__ import unicode_literals

from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=16)
	email    = models.EmailField()
	verified = models.BooleanField(default=False)
	level    = models.IntegerField(default=1)
	experience = models.IntegerField(default=0)
	created    = models.DateField(auto_now=False, auto_now_add=True)
	last_login = models.DateField(auto_now=False, auto_now_add=False)
	pref_grid  = models.IntegerField(default=100)