# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-31 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblatex', '0004_uploadedsong'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='attribution',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
