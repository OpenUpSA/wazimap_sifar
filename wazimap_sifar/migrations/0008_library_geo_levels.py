# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-11-27 12:27
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wazimap_sifar', '0007_auto_20181127_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='geo_levels',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, null=True, size=None),
        ),
    ]
