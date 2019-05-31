# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-13 14:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wazimap_sifar', '0017_auto_20190513_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contributer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.CharField(max_length=255)),
                ('approved', models.BooleanField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sifar_contributers',
            },
        ),
    ]
