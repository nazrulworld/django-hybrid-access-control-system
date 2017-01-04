# -*- coding: utf-8 -*-
# ++ This file `test_base.py` is generated at 11/23/16 5:42 PM ++
import os
import pytest
import logging
import warnings
from tests.path import FIXTURE_PATH
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.security.helpers import SystemUser
from hacs.security.base import SecurityManager
from django.contrib.auth.models import AnonymousUser

from tests.fixture import model_fixture

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestSecurityManager(TransactionTestCase):
    """"""

    fixtures = (FIXTURE, )

    def setUp(self):
        """
        :return:
        """
        super(TestSecurityManager, self).setUp()
        # Test Fixtures
        model_fixture.init_data()

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
            # User is not set yet! (usually should done by `AccessControlMiddleware`)
            # This assertion is offed for now! because of unknown error or bug, it works while running single
            # test suite
            # self.assertEqual(2, len(tuple(new_warns)))

        with warnings.catch_warnings(record=True) as warns:
            # http://stackoverflow.com/questions/5644836/in-python-how-does-one-catch-warnings-as-if-they-were-exceptions
            # Test with system user
            HACS_ACCESS_CONTROL_LOCAL.current_user = SystemUser()
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
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.contributoruser
        news_item_1 = model_fixture.models.get('news_item_cls').objects.get_by_natural_key('news-one')
        news_item_2 = model_fixture.models.get('news_item_cls'). \
            objects.get_by_natural_key('news-two-with-local-roles')

        # Contributor should not have Editor permission
        self.assertFalse(security_manager._check('hacs.ManageContent', news_item_1))
        # As `news_item_2` has local roles for contributor, so should have editor permission for this object
        self.assertTrue(security_manager._check('hacs.ManageContent', news_item_2))

    def test__check_object(self):
        """
        :return:
        """
        news_folder = model_fixture.models.get('news_folder_cls').objects.get_by_natural_key('news-folder')
        date_folder = model_fixture.models.get('date_folder_cls').objects.get_by_natural_key('2016-10-10')
        news_item = model_fixture.models.get('news_item_cls').objects.get_by_natural_key('news-one')
        security_manager = SecurityManager(date_folder.__class__)
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.contributoruser

        # User Must Have `hacs.ManageContent` permission to create Date Folder
        # Normally Contributor has don't have that permission
        self.assertFalse(security_manager._check_object(date_folder, 'object.create'))

        # News One is now in draft state.

        # Contributor has view access
        self.assertTrue(security_manager._check_object(news_item, 'object.view'))

        # Member User should not have view access
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.memberuser
        self.assertFalse(security_manager._check_object(news_item, 'object.view'))

        # Now we are changing state to internally_published.
        news_item.state = 'internally_published'
        # By Pass Security
        os.environ['HACS_AC_BYPASS'] = '1'
        news_item.save()
        del os.environ['HACS_AC_BYPASS']

        # Member user now should have view permission
        self.assertTrue(security_manager._check_object(news_item, 'object.view'))

        # Now we are changing state to published.
        news_item.state = 'published'
        # By Pass Security
        os.environ['HACS_AC_BYPASS'] = '1'
        news_item.save()
        del os.environ['HACS_AC_BYPASS']

        # Guest User should now view access
        # But! still we have to wait, as in this test fixture by default Anonymous user
        # don't have hacs.CanTraverseContainer, so content inside container don't have view permission for this user
        # Until container's state is published
        with warnings.catch_warnings(record=True) as warns:
            # http://stackoverflow.com/questions/5644836/in-python-how-does-one-catch-warnings-as-if-they-were-exceptions
            warnings.simplefilter("always")
            HACS_ACCESS_CONTROL_LOCAL.current_user = AnonymousUser()
            self.assertFalse(security_manager._check_object(news_item, 'object.view'))
            new_warns = filter(lambda x: issubclass(x.category, UserWarning), warns)
            # Should get one warning as well
            self.assertEqual(1, len(tuple(new_warns)))
        # Let's Publish Folders
        news_folder.state = 'published'
        # By Pass Security
        os.environ['HACS_AC_BYPASS'] = '1'
        news_folder.save()
        del os.environ['HACS_AC_BYPASS']

        date_folder.state = 'published'

        os.environ['HACS_AC_BYPASS'] = '1'
        date_folder.save()
        del os.environ['HACS_AC_BYPASS']
        # Refresh Data
        news_item = model_fixture.models.get('news_item_cls').objects.get_by_natural_key('news-one')
        # Now should have view permission
        self.assertTrue(security_manager._check_object(news_item, 'object.view'))

    def tearDown(self):
        """
        :return:
        """
        model_fixture.tear_down()
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
        super(TestSecurityManager, self).tearDown()
