# -*- coding: utf-8 -*-
# ++ This file `test_jsonb.py` is generated at 1/9/17 3:58 PM ++
import copy
from tests.path import FIXTURE_PATH
from tests.fixture import model_fixture
from django.test import TransactionTestCase
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.helpers import get_workflow_model
from hacs.security.helpers import attach_system_user
from hacs.security.helpers import release_system_user
from hacs.security.helpers import ANONYMOUS_USER
FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestJsonBUsecase(TransactionTestCase):
    """"""
    fixtures = (FIXTURE, )

    def setUp(self):
        """
        :return:
        """
        super(TestJsonBUsecase, self).setUp()
        model_fixture.init_data()

    def test_array_query(self):
        """
        :return:
        """
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsContent"])
        # should have two entries as both workflows have same permissions
        self.assertEqual(2, workflows.count())

        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsContent", "fake_key"])
        self.assertEqual(2, workflows.count())

        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsConte"])
        self.assertEqual(0, workflows.count())

        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsConte",
                                                                                   "fake_permission"])
        self.assertEqual(0, workflows.count())

        attach_system_user()
        workflow1 = get_workflow_model().objects.get(pk=1)
        workflow1.permissions = ["hacs.AuthenticatedView"]
        workflow1.save()
        release_system_user()

        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsContent"])
        self.assertEqual(1, workflows.count())

        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=["hacs.ManageUtilsContent", "hacs.AuthenticatedView"])
        self.assertEqual(2, workflows.count())

        # ** Let's with user
        permissions = model_fixture.memberuser.get_all_permissions()
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=permissions)
        # Should one because we allowed AuthenticatedView
        self.assertEqual(1, workflows.count())
        workflows = get_workflow_model().objects.filter(permissions__contained_by=list(permissions))
        self.assertEqual(1, workflows.count())
        # Anonymous user should not have permissions
        permissions = ANONYMOUS_USER.get_all_permissions()
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=permissions)
        self.assertEqual(0, workflows.count())

        # Let's changed permissions
        attach_system_user()
        workflow1 = get_workflow_model().objects.get(pk=1)
        workflow1.permissions = ["hacs.ManagePortal"]
        workflow1.save()
        release_system_user()

        permissions = model_fixture.memberuser.get_all_permissions()
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=permissions)
        # no permissions for member user
        self.assertEqual(0, workflows.count())

        permissions = model_fixture.editoruser.get_all_permissions()
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=permissions)
        # no permission for editor user also
        self.assertEqual(0, workflows.count())

        permissions = model_fixture.superuser.get_all_permissions()
        workflows = get_workflow_model().objects.filter(permissions__has_any_keys=permissions)
        # should have two workflow access
        self.assertEqual(2, workflows.count())
        workflows = get_workflow_model().objects.filter(permissions__contained_by=list(permissions))
        self.assertEqual(2, workflows.count())

    def test_dict_query(self):
        """
        :return:
        """
        date_folder_cls = model_fixture.models.get('date_folder_cls')

        # All normal tries
        results = date_folder_cls.objects.filter(permissions_actions_map__has_key="object.view")
        self.assertEqual(1, results.count())

        results = date_folder_cls.objects.filter(permissions_actions_map__has_key="object.fake")
        self.assertEqual(0, results.count())

        results = date_folder_cls.objects.filter(permissions_actions_map__has_any_keys=["object.fake", "object.delete"])
        self.assertEqual(1, results.count())

        results = date_folder_cls.objects.filter(permissions_actions_map__has_keys=["object.fake", "object.delete"])
        self.assertEqual(0, results.count())
        results = date_folder_cls.objects.filter(permissions_actions_map__has_keys=["object.view", "object.delete"])
        self.assertEqual(1, results.count())

        # Try with level 1 key path search
        _filter = {
            "permissions_actions_map__object.view__has_key": "hacs.ViewContent"
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())
        # Try with invalid path
        _filter = {
            "permissions_actions_map__object.fake__has_key": "hacs.ViewContent"
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        _filter = {
            "permissions_actions_map__object.view__contains": ["hacs.ViewContent"]
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__contained_by": ["hacs.ViewContent", "hacs.Fake",
                                                                   "hacs.ManageUtilsContent"]
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__contained_by": ["hacs.ManagePortal", "hacs.Fake",
                                                                   "hacs.ManageUtilsContent"]
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        _filter = {
            "permissions_actions_map__object.view__has_any_keys": ["hacs.ViewContent", "hacs.Fake",
                                                                   "hacs.ManageUtilsContent"]
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__has_any_keys": ["hacs.ManagePortal", "hacs.Fake",
                                                                   "hacs.ManageUtilsContent"]
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        # Test with user
        _filter = {
            "permissions_actions_map__object.view__has_any_keys": model_fixture.memberuser.get_all_permissions()
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        _filter = {
            "permissions_actions_map__object.view__contained_by": list(model_fixture.memberuser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        _filter = {
            "permissions_actions_map__object.view__has_any_keys": model_fixture.contributoruser.get_all_permissions()
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__contained_by": list(model_fixture.contributoruser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__has_any_keys": model_fixture.editoruser.get_all_permissions()
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__object.view__contained_by": list(
                model_fixture.editoruser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        # Test With 3rd Level path search
        date_folder = date_folder_cls.objects.get(pk=1)
        date_folder.permissions_actions_map.update({
            "hacs.action": {
                "level2": {
                    "level3": date_folder.permissions_actions_map['object.view']
                }
            }
        })

        attach_system_user()
        date_folder.save()
        release_system_user()
        _filter = {
            "permissions_actions_map__hacs.action__level2__level3__contained_by": list(
                model_fixture.editoruser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__hacs.action__level2__level3__has_any_keys": model_fixture.editoruser.get_all_permissions()
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(1, results.count())

        _filter = {
            "permissions_actions_map__hacs.action__level2__level3__contained_by": list(
                model_fixture.memberuser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

        _filter = {
            "permissions_actions_map__object.view__level2__level3__contained_by": list(
                model_fixture.editoruser.get_all_permissions())
        }
        results = date_folder_cls.objects.filter(**_filter)
        self.assertEqual(0, results.count())

    def tearDown(self):
        """"""
        model_fixture.tear_down()
        super(TestJsonBUsecase, self).tearDown()
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
