# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/11/16 2:44 PM ++
import pytest
import copy
from collections import defaultdict
from tests.path import FIXTURE_PATH
from django.test import TransactionTestCase
from django.contrib.contenttypes.models import ContentType
from hacs.models import HacsContentType
from django.contrib.auth import get_user_model
from hacs.defaults import HACS_DEFAULT_STATE
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.security.helpers import attach_system_user
from hacs.security.helpers import release_system_user
from django.core.exceptions import PermissionDenied
from tests.fixture import model_fixture

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsContainerModel(TransactionTestCase):
    """
    """
    fixtures = (FIXTURE,)

    def setUp(self):

        super(TestHacsContainerModel, self).setUp()
        model_fixture.init_data()

    def test__save_table(self):

        superuser = get_user_model().objects.get_by_natural_key("manager@test.com")

        #################
        ## INSERT TEST ##
        #################
        news_folder_cls = model_fixture.models.get('news_folder_cls')
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
        local_roles = {"contributor@test.com": ["Editor", ]}
        date_folder_cls = model_fixture.models.get('date_folder_cls')
        data = {
            "name": "2016-12-12",
            "slug": "2016-12-12",
            "description": "12th December, 2016",
            "created_by": superuser,
            "local_roles": local_roles,
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
        news_item_cls = model_fixture.models.get('news_item_cls')
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

        # Test Local Roles inherit from DateFolder
        self.assertEqual(local_roles, news_item.local_roles)
        # Let's clean all
        news_folder.delete()

        # Test Recursive Works
        news_folder_cls = model_fixture.models.get('news_folder_cls')
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

        date_folder_cls = model_fixture.models.get('date_folder_cls')
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

        # Create News Item at Site Root (item without container folder)
        data = {
            "name": "test news one at site root",
            "slug": "test-news-one-at-site",
            "description": "test news of HACS inside site root",
            "created_by": contributor,
            "owner": contributor,
            "acquire_parent": False,
            "container_content_type": None,
            "container_id": None
        }
        news_item = news_item_cls(**data)
        # Should Not Save, globally not allowed
        # This constraint check should be done by validator not responsible by BaseModel
        news_item.save()

    def test_delete(self):
        """
        :return:
        """
        news_item_cls = model_fixture.models.get('news_item_cls')
        date_folder_cls = model_fixture.models.get('date_folder_cls')
        news_item_1 = news_item_cls.objects.get_by_natural_key('news-one')
        news_item_1_copy = copy.copy(news_item_1)
        news_item_2 = news_item_cls.objects.get_by_natural_key('news-two-with-local-roles')
        news_item_2_copy = copy.copy(news_item_2)
        date_folder1 = date_folder_cls.objects.get_by_natural_key('2016-10-10')
        date_folder1_copy = copy.copy(date_folder1)
        contributor2 = get_user_model().objects.get_by_natural_key('contributor2@test.com')
        # As we have one record
        self.assertGreater(news_item_cls.objects.count(), 0)
        self.assertGreater(date_folder_cls.objects.count(), 0)

        # Test delete security guard
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.memberuser
        try:
            news_item_1_copy.delete()
            raise AssertionError("Code should not come here as member user don't have permission to delete any content")
        except PermissionDenied:
            pass

        HACS_ACCESS_CONTROL_LOCAL.current_user = contributor2
        try:
            news_item_1_copy.delete()
            raise AssertionError("Code should not come here as contributor user also don't has permission to "
                                 "delete any content")
        except PermissionDenied:
            pass

        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.contributoruser
        try:
            news_item_1_copy.delete()
            # re-insert for further test
            attach_system_user()
            news_item_1.save()
            release_system_user()

            news_item_1_copy = copy.copy(news_item_1)
        except PermissionDenied:
            raise AssertionError("Code should not come here as although contributor user don't has permission to "
                                 "delete any content but this certain contributor owner of this content")

        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.editoruser
        try:
            news_item_1_copy.delete()
            # re-insert for further test
            attach_system_user()
            news_item_1.save()
            release_system_user()

            news_item_1_copy = copy.copy(news_item_1)
        except PermissionDenied:
            raise AssertionError("Code should not come here as editor user has permission to "
                                 "delete any content")

        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.superuser
        try:
            news_item_1_copy.delete()
            # re-insert for further test

            attach_system_user()
            news_item_1.save()
            release_system_user()

            news_item_1_copy = copy.copy(news_item_1)
        except PermissionDenied:
            raise AssertionError("Code should not come here as super user can perform any action")

        # Test with local roles
        # Contributor user has local role Editor on news_item2
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.contributoruser
        try:
            news_item_2_copy.delete()

            attach_system_user()
            news_item_2.save()
            release_system_user()

            news_item_2_copy = copy.copy(news_item_2)
        except PermissionDenied:
            raise AssertionError("Code should not come here, because contributor user has local role editor")

        # Test By changing workflow state
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.editoruser
        try:
            date_folder1_copy.delete()

            attach_system_user()
            date_folder1.save()
            release_system_user()

        except PermissionDenied:
            raise AssertionError("Code should not come here, as editor user should have permission to delete.")
        date_folder1.state = 'published'

        attach_system_user()
        date_folder1.save()
        release_system_user()

        date_folder1_copy = copy.copy(date_folder1)

        try:
            date_folder1_copy.delete()
            raise AssertionError("Code should not come here, as state changed to published, not"
                                 " `hacs.ManagePortal` permission holder can delete")
        except PermissionDenied:
            pass

        date_folder1_copy.owner = model_fixture.editoruser

        attach_system_user()
        date_folder1_copy.save()
        release_system_user()

        try:
            date_folder1_copy.delete()

            attach_system_user()
            date_folder1.save()
            release_system_user()
            date_folder1_copy = copy.copy(date_folder1)
        except PermissionDenied:
            raise AssertionError("Code should not come here, as owner changed to editor user,"
                                 "can delete")

        # Testing Children removed before parent container moved
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
        news_folder_cls = model_fixture.models.get('news_folder_cls')
        news_folder = news_folder_cls.objects.all().first()
        news_folder.delete()

        # No records should be, as cascade applied
        self.assertEqual(news_item_cls.objects.count(), 0)
        self.assertEqual(date_folder_cls.objects.count(), 0)

    def tearDown(self):
        """
        :return:
        """
        model_fixture.tear_down()
        super(TestHacsContainerModel, self).tearDown()
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
