# -*- coding: utf-8 -*-
# ++ This file `context_processors.py` is generated at 6/22/16 7:20 PM ++
from __future__ import unicode_literals
from django.conf import settings
from .defaults import HACS_DEVELOPMENT_MODE

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


def hacs_development_mode(request):
    """"""
    return {
        "HACS_DEVELOPMENT_MODE": getattr(settings, 'HACS_DEVELOPMENT_MODE', HACS_DEVELOPMENT_MODE)
    }
