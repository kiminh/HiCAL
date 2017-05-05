# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-03 03:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topic', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='current_topic',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='topic.Topic'),
            preserve_default=False,
        ),
    ]
