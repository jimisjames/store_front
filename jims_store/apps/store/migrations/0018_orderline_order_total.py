# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-27 22:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_remove_orderline_date_ordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderline',
            name='order_total',
            field=models.IntegerField(default=1000),
            preserve_default=False,
        ),
    ]
