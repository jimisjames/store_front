# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-27 22:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_orderline_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='product_price',
            field=models.IntegerField(),
        ),
    ]