# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-31 09:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblatex', '0002_auto_20151227_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='attribution',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
