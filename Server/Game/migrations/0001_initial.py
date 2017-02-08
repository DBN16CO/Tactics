# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-05 00:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Static', '0001_initial'),
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_round', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_move', models.DateTimeField(auto_now=True)),
                ('finished', models.BooleanField(default=False)),
                ('map_path', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Map')),
                ('user_turn', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='User.Users')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version')),
            ],
        ),
        migrations.CreateModel(
            name='Game_Queue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='User.Users')),
            ],
        ),
        migrations.CreateModel(
            name='Game_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=25, null=True)),
                ('team', models.IntegerField(default=0)),
                ('victorious', models.BooleanField(default=False)),
                ('game', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Game.Game')),
                ('leader_abil', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Leader_Ability')),
                ('perk_1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='perk_1', to='Static.Perk')),
                ('perk_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='perk_2', to='Static.Perk')),
                ('perk_3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='perk_3', to='Static.Perk')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='User.Users')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hp', models.IntegerField(default=0)),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('game', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Game.Game')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='User.Users')),
                ('target', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='Game.Unit')),
                ('unit_class', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Class')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='game_user',
            unique_together=set([('name', 'user')]),
        ),
    ]
