# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-06-04 02:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0007_auto_20200528_1346'),
        ('judgment', '0002_judgement_task'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Task',
            new_name='Session',
        ),
    ]
