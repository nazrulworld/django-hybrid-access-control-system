# -*- coding: utf-8 -*-
# ++ This file `test_jsonb.py` is generated at 1/9/17 3:58 PM ++
import copy
from tests.path import FIXTURE_PATH
from tests.fixture import model_fixture
from django.test import TransactionTestCase
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.helpers import get_workflow_model
from django.db import transaction
from hacs.security.helpers import attach_system_user
from hacs.security.helpers import release_system_user

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






    def tearDown(self):
        """"""
        model_fixture.tear_down()
        super(TestJsonBUsecase, self).tearDown()
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
