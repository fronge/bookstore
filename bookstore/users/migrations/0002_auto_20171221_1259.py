# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-21 12:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['create_time']},
        ),
    ]