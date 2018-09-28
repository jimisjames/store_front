# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-27 19:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_auto_20180927_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='store.User'),
        ),
    ]
