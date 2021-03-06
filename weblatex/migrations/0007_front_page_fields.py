# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 21:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblatex', '0006_bookletentry_attribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='booklet',
            name='contents',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='booklet',
            name='front_image',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='booklet',
            name='front_text',
            field=models.TextField(blank=True),
        ),
    ]
