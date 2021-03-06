# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-27 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_auto_20180927_1941'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderline',
            old_name='order_total',
            new_name='pre_tax_order_total',
        ),
        migrations.RenameField(
            model_name='orderline',
            old_name='pre_tax',
            new_name='pre_tax_product_total',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='tax',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='total',
        ),
        migrations.AlterField(
            model_name='orderline',
            name='ship_to',
            field=models.TextField(),
        ),
    ]
