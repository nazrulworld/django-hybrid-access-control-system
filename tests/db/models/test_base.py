# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/11/16 2:44 PM ++
import pytest
from collections import defaultdict
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.db import connection
from hacs.db.models.base import HacsItemModel, HacsContainerModel, HacsUtilsModel
from django.contrib.auth import get_user_model

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


def setupModels(*models):
    """
    :param models:
    :return:
    """
    with connection.schema_editor(atomic=True) as schema_editor:
        for model in models:
            schema_editor.create_model(model)


def get_models():

    class TestContainerModel(HacsContainerModel):
        class Meta:
            app_label = "hacs"
            db_table = "test_base_container"
            globally_allowed = True

    class TestItemModel(HacsItemModel):
        class Meta:
            app_label = "hacs"
            db_table = "test_base_item"

    class TestUitilsModel(HacsUtilsModel):
        class Meta:
            app_label = "hacs"
            db_table = "test_base_utils"

    return {
        'container': TestContainerModel,
        'item': TestItemModel,
        'utils': TestUitilsModel
    }


class TestHacsContainerModel(TestCase):
    """
    """
    fixtures = (FIXTURE,)

    def setUp(self):

        super(TestHacsContainerModel, self).setUp()
        self.models = get_models()
        setupModels(*self.models.values())

    def test__save_table(self):
        user = get_user_model().objects.first()
        container_cls = self.models.get('container')
        data = {
            "name": "test container",
            "slug": "test-container",
            "created_by": user,
            "modified_by": user,
            "state": "Initilized",
            "permissions_actions_map": None,
            #"local_roles": None,
            "owner": user,
            "acquire_parent": True,
            "workflow": None,
            "container_content_type": None,
            "parent_container_id": None,
            "recursive": False,
            "description": None
        }

        container = container_cls(**data)
        container.save()
        container.state = "Changed"
        container.save()
