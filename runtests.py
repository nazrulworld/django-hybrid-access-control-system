#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ++ This file `runtests.py` is generated at 5/20/16 7:18 PM ++
import os
import re
import sys
import django
import pytest
import tempfile
from django.conf import settings
from django.conf import global_settings

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DJANGO_SETTINGS= {

    'INSTALLED_APPS': [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'hacs.apps.HACSConfig',
    ],

    'MIDDLEWARE_CLASSES': [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(tempfile.gettempdir(), 'hacs_test_db.sqlite3'),
        }
    },
    'ROOT_URLCONF': 'hacs.urls',
    'SECRET_KEY': '-5j*j+w!-58!*zlq!ofk%80i-0ejb()$o8vz$af&lv-prnc29b',
    'DEBUG': True,
    'ALLOWED_HOSTS': ['*'],
    'LANGUAGE_CODE': 'en-us',
    'TIME_ZONE': 'UTC',
    'USE_I18N': True,
    'USE_L10N': True,
    'USE_TZ': True,
    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    'STATIC_URL':  '/static/'

}

def setup_django_env():
    """"""
    settings.configure(global_settings, **DJANGO_SETTINGS)
    django.setup()


if __name__ == '__main__':

    setup_django_env()
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    if len(sys.argv) > 1:
        for member in ('-s', '-rw'):
            if member not in sys.argv:
                sys.argv.append(member)

    sys.exit(pytest.main())


