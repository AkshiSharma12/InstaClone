# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 06:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instaclone', '0011_auto_20170722_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postmodel',
            name='category',
        ),
    ]
