# -*- coding: utf-8 -*-
# ++ This file `signals.py` is generated at 2/15/17 7:52 PM ++
from django.db.models.signals import ModelSignal

__author__ = 'Md Nazrul Islam<connect2nazrul@gmail.com>'

queryset_update = ModelSignal(providing_args=["queryset", "update_kwargs"], use_caching=True)

