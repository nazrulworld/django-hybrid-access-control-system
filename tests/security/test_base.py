# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/23/16 5:42 PM ++
import pytest
import logging
import warnings
from collections import defaultdict
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.db import connection
from hacs.db.models.base import HacsItemModel, HacsContainerModel, HacsUtilsModel
from django.contrib.auth import get_user_model
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.models import HacsSystemUser
from hacs.security.base import SecurityManager

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestSecurityManager(TestCase):
    """"""

    fixtures = (FIXTURE, )

    def setUp(self):
        """
        :return:
        """
        return super(TestSecurityManager, self).setUp()

    def test_check(self):
        """
        :return:
        """
        # enable us to capture any warns happen
        logging.captureWarnings(False)

        security_manager = SecurityManager()

        with warnings.catch_warnings(record=True) as warns:
            # http://stackoverflow.com/questions/5644836/in-python-how-does-one-catch-warnings-as-if-they-were-exceptions

            warnings.simplefilter("always")
            security_manager._check('hacs.ManagePortal')
            new_warns = filter(lambda x: issubclass(x.category, UserWarning), warns)
            # Should be two warnings. one. get_ac_user() two. _check()
            # User is not set yet! (usally should done by `AccessControlMiddleware`)
            self.assertEqual(2, len(tuple(new_warns)))

        with warnings.catch_warnings(record=True) as warns:
            # http://stackoverflow.com/questions/5644836/in-python-how-does-one-catch-warnings-as-if-they-were-exceptions
            # Test with system user
            HACS_ACCESS_CONTROL_LOCAL.current_user = HacsSystemUser()
            warnings.simplefilter("always")
            # should have permission without any complain because of system user
            self.assertTrue(security_manager._check('hacs.ManagePortal'))
            new_warns = filter(lambda x: issubclass(x.category, UserWarning), warns)
            # Should not any warnings
            # System User is set! (usally should done by `AccessControlMiddleware`)

            self.assertEqual(0, len(tuple(new_warns)))
