# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-04 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('axf', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='price',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='goods',
            name='specifics',
            field=models.CharField(max_length=20),
        ),
    ]
