from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Version(models.Model):
	name         = models.CharField(max_length=16, unique=True)
	
class Action(models.Model):	
	name         = models.CharField(max_length=16)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)
	description  = models.CharField(max_length=100)

	class Meta:
		unique_together = ('name', 'version')

class Class(models.Model):	
	name         = models.CharField(max_length=16)
	description  = models.CharField(max_length=100)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'version')

class Hero_Ability(models.Model):
	name         = models.CharField(max_length=16)
	description  = models.CharField(max_length=100)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'version')

class Leader(models.Model):	
	name         = models.CharField(max_length=16)
	ability      = models.ForeignKey(Hero_Ability, on_delete=models.DO_NOTHING)
	description  = models.CharField(max_length=100)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'ability', 'version')

class Perk(models.Model):
	name         = models.CharField(max_length=16)
	description  = models.CharField(max_length=100)
	tier         = models.IntegerField(default=100)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'version')

class Map(models.Model):
	name         = models.CharField(max_length=16)	
	file_path    = models.CharField(max_length=128)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('file_path', 'version')

class Stat(models.Model):
	name         = models.CharField(max_length=16)   # HP, Strength, Agility
	unit         = models.ForeignKey(Class,        on_delete=models.DO_NOTHING)
	value        = models.FloatField(default=0)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'unit', 'version')

class Terrain(models.Model):
	name		 = models.CharField(max_length=16)	# Mountain, Grass, Road
	unit         = models.ForeignKey(Class,        on_delete=models.DO_NOTHING)
	move         = models.FloatField(default=1.0)
	shortname    = models.CharField(max_length=8)
	version      = models.ForeignKey(Version,      on_delete=models.DO_NOTHING)

	class Meta:
		unique_together = ('name', 'unit', 'version')

