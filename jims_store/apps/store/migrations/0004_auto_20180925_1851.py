# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-25 18:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20180925_1743'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='photo_name',
            new_name='name',
        ),
    ]
