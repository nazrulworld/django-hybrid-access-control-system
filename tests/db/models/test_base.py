# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/11/16 2:44 PM ++
import pytest
from collections import defaultdict
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from hacs.models import HacsContentType
from django.contrib.auth import get_user_model
from hacs.defaults import HACS_DEFAULT_STATE

from tests.fixture import ModelFixture

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsContainerModel(TestCase):
    """
    """
    fixtures = (FIXTURE,)
    model_fixture = ModelFixture()

    def setUp(self):

        super(TestHacsContainerModel, self).setUp()
        self.model_fixture.init_data()

    def test__save_table(self):

        superuser = get_user_model().objects.get_by_natural_key("manager@test.com")

        #################
        ## INSERT TEST ##
        #################
        news_folder_cls = self.model_fixture.models.get('news_folder_cls')
        data = {
            "name": "test news folder",
            "slug": "test-news-folder",
            "description": "News Folder",
            "created_by": superuser,
            "owner": superuser,
            "acquire_parent": False,
            "workflow": None,
            "container_content_type": None,
            "parent_container_id": None,
            "recursive": True
        }

        news_folder = news_folder_cls(**data)
        news_folder.save()

        date_folder_cls = self.model_fixture.models.get('date_folder_cls')
        data = {
            "name": "2016-12-12",
            "slug": "2016-12-12",
            "description": "12th December, 2016",
            "created_by": superuser,
            "local_roles": {"contributor@test.com": ("Editor", )},
            "owner": superuser,
            "acquire_parent": True,
            "workflow": None,
            "container_content_type": ContentType.objects.get_for_model(news_folder_cls),
            "parent_container_id": news_folder.pk,
            "recursive": True
        }

        date_folder = date_folder_cls(**data)
        date_folder.save()

        contributor = get_user_model().objects.get_by_natural_key("contributor@test.com")
        news_item_cls = self.model_fixture.models.get('news_item_cls')
        news_item_ct = HacsContentType.objects.get_for_model(news_item_cls)
        data = {
            "name": "test news one",
            "slug": "test-news-one",
            "description": "test news of HACS",
            "created_by": contributor,
            "owner": contributor,
            "acquire_parent": True,
            "container_content_type": ContentType.objects.get_for_model(date_folder_cls),
            "container_id": date_folder.pk
        }
        news_item = news_item_cls(**data)
        news_item.save()

        # Test State and Permission map is populated
        # make state is updated
        self.assertIsNotNone(news_folder.state)
        self.assertEqual(news_folder.state, HACS_DEFAULT_STATE)

        # Make sure permission map is populated
        self.assertIsNotNone(news_folder.permissions_actions_map)
        # We Test permissions map come from workflow
        news_folder_ct = HacsContentType.objects.get_for_model(news_folder_cls)
        self.assertEqual(news_folder.permissions_actions_map, news_folder_ct.workflow.states_permissions_map[news_folder.state])
        # Should get workflow also
        self.assertIsNotNone(date_folder.workflow)
        self.assertEqual(news_folder.workflow, date_folder.workflow)
        # News Item workflow must be different
        self.assertNotEqual(news_item_ct.workflow, date_folder.workflow)
        # Let's clean all
        news_folder.delete()

        # Test Recursive Works
        news_folder_cls = self.model_fixture.models.get('news_folder_cls')
        data = {
            "name": "test news folder 2",
            "slug": "test-news-folder-2",
            "description": "News Folder 2",
            "created_by": superuser,
            "owner": superuser,
            "acquire_parent": False,
            "workflow": None,
            "container_content_type": None,
            "parent_container_id": None,
            "recursive": False
        }

        news_folder = news_folder_cls(**data)
        news_folder.save()

        date_folder_cls = self.model_fixture.models.get('date_folder_cls')
        data = {
            "name": "2016-12-12-2",
            "slug": "2016-12-12-2",
            "description": "12-2th December, 2016",
            "created_by": superuser,
            "local_roles": {"contributor@test.com": ("Editor",)},
            "owner": superuser,
            "acquire_parent": True,
            "workflow": None,
            "container_content_type": ContentType.objects.get_for_model(news_folder_cls),
            "parent_container_id": news_folder.pk,
            "recursive": True
        }

        date_folder = date_folder_cls(**data)
        date_folder.save()

        # Should not get workflow, although `acquire_parent` is true but respected parent recursive status!
        self.assertIsNone(date_folder.workflow)

    def test_delete(self):
        """
        :return:
        """
        news_item_cls = self.model_fixture.models.get('news_item_cls')
        date_folder_cls = self.model_fixture.models.get('date_folder_cls')
        # As we have one record
        self.assertGreater(news_item_cls.objects.count(), 0)
        self.assertGreater(date_folder_cls.objects.count(), 0)
        # Testing Children removed before parent container moved
        news_folder_cls = self.model_fixture.models.get('news_folder_cls')
        news_folder = news_folder_cls.objects.all().first()
        news_folder.delete()

        # No records should be, as cascade applied
        self.assertEqual(news_item_cls.objects.count(), 0)
        self.assertEqual(date_folder_cls.objects.count(), 0)
