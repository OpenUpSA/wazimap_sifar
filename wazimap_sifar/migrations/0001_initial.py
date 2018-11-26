# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-11-21 13:34
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrivatePharmacy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(blank=True, max_length=100)),
                ('district', models.CharField(blank=True, max_length=100)),
                ('sub_district', models.CharField(blank=True, max_length=100)),
                ('facility', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('address', models.CharField(blank=True, max_length=200)),
                ('organization_unit', models.CharField(blank=True, max_length=200)),
                ('organization_unit_type', models.CharField(blank=True, max_length=200)),
                ('geo_levels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, null=True, size=None)),
            ],
            options={
                'db_table': 'private_pharmacy',
                'verbose_name_plural': 'private pharmacies',
            },
        ),
        migrations.AlterUniqueTogether(
            name='privatepharmacy',
            unique_together=set([('facility', 'latitude', 'longitude', 'organization_unit_type')]),
        ),
    ]
