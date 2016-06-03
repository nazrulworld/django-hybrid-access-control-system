# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-01 16:27
from __future__ import unicode_literals

from django.db import migrations
import hacs.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hacs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='routingtable',
            name='allowed_method',
            field=hacs.fields.SequenceField(blank=True, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('HEAD', 'HEAD'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE'), ('OPTIONS', 'OPTIONS')], null=True, verbose_name='Allowed Method'),
        ),
    ]