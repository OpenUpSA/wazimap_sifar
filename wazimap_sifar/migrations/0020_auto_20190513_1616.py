# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-13 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wazimap_sifar', '0019_auto_20190513_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributer',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]