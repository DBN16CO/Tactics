from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Version(models.Model):
	name         = models.CharField(max_length=16)
	
class Action(models.Model):	
	name         = models.CharField(max_length=16)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Class(models.Model):	
	name         = models.CharField(max_length=16)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Hero_Ability(models.Model):
	name         = models.CharField(max_length=16)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Leader(models.Model):	
	name         = models.CharField(max_length=16)
	ability      = models.ForeignKey(Hero_Ability, on_delete=models.DO_NOTHING)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Perk(models.Model):
	name         = models.CharField(max_length=16)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Map(models.Model):	
	file_path    = models.CharField(max_length=128)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

class Stat(models.Model):
	name         = models.CharField(max_length=16)   # HP, Strength, Agility
	unit         = models.ForeignKey(Class,        on_delete=models.DO_NOTHING)
	value        = models.IntegerField(default=0)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

