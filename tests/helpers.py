# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 12/10/16 3:12 PM ++
from django.db import connection
from django.db import DEFAULT_DB_ALIAS
from django.contrib.contenttypes.models import ContentType
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


def setupModels(*models):
    """
    :param models:
    :return:
    """
    with connection.schema_editor(atomic=True) as schema_editor:
        for model in models:
            schema_editor.create_model(model)

    cts = [ContentType(app_label=model._meta.app_label, model=model._meta.model) for model in models]
    ContentType.objects.using(DEFAULT_DB_ALIAS).bulk_create(cts)


def tearDownModels(*models):
    """
    :param models:
    :return:
    """
    with connection.schema_editor(atomic=True) as schema_editor:
        for model in models:
            schema_editor.delete_model(model)
