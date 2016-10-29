# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 05:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Hero_Ability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Leader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Hero_Ability')),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Perk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('value', models.IntegerField(default=0)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Class')),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.AddField(
            model_name='stat',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='perk',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='map',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='leader',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='hero_ability',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='class',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
        migrations.AddField(
            model_name='action',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='Static.Version'),
        ),
    ]
