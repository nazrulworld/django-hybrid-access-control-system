# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/23/16 5:42 PM ++
import pytest
import logging
import warnings
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.contrib.auth import get_user_model
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.models import HacsSystemUser
from hacs.db.models import HacsItemModel
from hacs.db.models import HacsContainerModel
from hacs.security.base import SecurityManager

from tests.fixture import ModelFixture

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestSecurityManager(TestCase):
    """"""

    fixtures = (FIXTURE, )
    model_fixture = ModelFixture()

    def setUp(self):
        """
        :return:
        """
        super(TestSecurityManager, self).setUp()
        # Test Fixtures
        self.model_fixture.init_data()

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
            # System User is set! (usually should done by `AccessControlMiddleware`)

            self.assertEqual(0, len(tuple(new_warns)))
            # Let's clean up user
            HACS_ACCESS_CONTROL_LOCAL.__release_local__()
            # Test If Release local is working
            try:
                HACS_ACCESS_CONTROL_LOCAL.current_user
            except AttributeError:
                pass
            else:
                AssertionError("Code should not come here! as should raise attribute error after release local")

        superuser = get_user_model().objects.get_by_natural_key('superuser@test.com')
        memberuser = get_user_model().objects.get_by_natural_key('member@test.com')

        HACS_ACCESS_CONTROL_LOCAL.current_user = superuser
        # Test superuser has permissions
        self.assertTrue(security_manager._check('hacs.ManagePortal'))
        HACS_ACCESS_CONTROL_LOCAL.current_user = memberuser
        # Test member user has no permissions of course
        self.assertFalse(security_manager._check('hacs.ManagePortal'))

        # Test with multiple permissions
        # Test member user should have permission now
        self.assertTrue(security_manager._check(('hacs.ManagePortal', 'hacs.AuthenticatedView',)))

        # Test with object and local roles
        HACS_ACCESS_CONTROL_LOCAL.current_user = self.model_fixture.contributoruser
        news_item_1 = self.model_fixture.models.get('news_item_cls').objects.get_by_natural_key('news-one')
        news_item_2 = self.model_fixture.models.get('news_item_cls'). \
            objects.get_by_natural_key('news-two-with-local-roles')

        # Contributor should not have Editor permission
        self.assertFalse(security_manager._check('hacs.ManageContent', news_item_1))
        # As `news_item_2` has local roles for contributor, so should have editor permission for this object
        self.assertTrue(security_manager._check('hacs.ManageContent', news_item_2))

    def test__check_object(self):
        """
        :return:
        """
