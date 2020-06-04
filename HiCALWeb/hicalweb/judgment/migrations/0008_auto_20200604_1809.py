# Generated by Django 3.0.5 on 2020-06-04 22:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('progress', '0008_auto_20200603_2255'),
        ('judgment', '0007_auto_20200531_2359'),
    ]

    operations = [
        migrations.RenameField(
            model_name='judgment',
            old_name='task',
            new_name='session',
        ),
        migrations.AlterUniqueTogether(
            name='judgment',
            unique_together={('user', 'doc_id', 'session')},
        ),
        migrations.AlterIndexTogether(
            name='judgment',
            index_together={('user', 'doc_id', 'session')},
        ),
    ]