from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Action_History(models.Model):
	order        = models.IntegerField()
	game         = models.ForeignKey('Game',          on_delete=models.DO_NOTHING)
	turn_number  = models.IntegerField()
	acting_user  = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	acting_unit  = models.ForeignKey('Game.Unit',     on_delete=models.DO_NOTHING, related_name='acting_unit')
	action       = models.ForeignKey('Static.Action', on_delete=models.DO_NOTHING)
	old_x        = models.IntegerField()
	new_x        = models.IntegerField()
	old_y        = models.IntegerField()
	new_y        = models.IntegerField()
	old_hp       = models.IntegerField()
	new_hp       = models.IntegerField(default=-1)
	unit_missed  = models.BooleanField(default=False)
	unit_crit    = models.BooleanField(default=False)
	target       = models.ForeignKey('Game.Unit',     on_delete=models.DO_NOTHING, null=True, default=None, related_name='action_target')
	tgt_old_hp   = models.IntegerField(default=-1)
	tgt_new_hp   = models.IntegerField(default=-1)
	tgt_counter  = models.BooleanField(default=False)
	tgt_missed   = models.BooleanField(default=False)
	tgt_crit     = models.BooleanField(default=False)
	created      = models.DateTimeField(auto_now_add=True)

	class meta:
		unique_together = ('order', 'game')

class Game(models.Model):
	game_round   = models.IntegerField(default=1)
	user_turn    = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	map_path     = models.ForeignKey('Static.Map',    on_delete=models.DO_NOTHING)
	created      = models.DateTimeField(auto_now_add=True)
	last_move    = models.DateTimeField(auto_now=True)
	finished     = models.BooleanField(default=False)
	version      = models.ForeignKey('Static.Version',on_delete=models.DO_NOTHING)

class Game_Queue(models.Model):
	user         = models.OneToOneField('User.Users', on_delete=models.DO_NOTHING)
	created      = models.DateTimeField(auto_now_add=True)
	updated      = models.DateTimeField(auto_now=True)

class Game_User(models.Model):
	game         = models.ForeignKey(Game,   		  on_delete=models.DO_NOTHING, null=True, default=None)
	name         = models.CharField(max_length=25, null=True, default=None)
	user         = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	team         = models.IntegerField(default=0)
	leader_abil  = models.ForeignKey('Static.Leader_Ability', on_delete=models.DO_NOTHING)
	perk_1       = models.ForeignKey('Static.Perk',   on_delete=models.DO_NOTHING, null=True, related_name='perk_1')
	perk_2       = models.ForeignKey('Static.Perk',   on_delete=models.DO_NOTHING, null=True, related_name='perk_2')
	perk_3       = models.ForeignKey('Static.Perk',   on_delete=models.DO_NOTHING, null=True, related_name='perk_3')
	victorious   = models.BooleanField(default=False)

	class Meta:
		unique_together = ('name', 'user')

class Unit(models.Model):
	unit_class   = models.ForeignKey('Static.Class',  on_delete=models.DO_NOTHING)
	acted        = models.BooleanField(default=False)
	hp           = models.IntegerField(default=0)
	x            = models.IntegerField(default=-1)
	y            = models.IntegerField(default=-1)
	target       = models.ForeignKey('self',          on_delete=models.DO_NOTHING, null=True, default=None)
	owner        = models.ForeignKey('User.Users',    on_delete=models.DO_NOTHING)
	game         = models.ForeignKey('Game',          on_delete=models.DO_NOTHING, null=True, default=None)
	version      = models.ForeignKey('Static.Version',on_delete=models.DO_NOTHING)
