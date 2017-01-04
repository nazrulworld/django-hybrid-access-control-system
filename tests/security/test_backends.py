# -*- coding: utf-8 -*-
# ++ This file `test_backends.py` is generated at 11/23/16 5:43 PM ++

import pytest
from django.conf import settings
from django.core.cache import caches
from tests.path import FIXTURE_PATH
from django.test import TransactionTestCase
from hacs.models import HacsPermissionModel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.security.helpers import get_cache_key
from hacs.security.backends import HacsAuthorizerBackend
from hacs.helpers import get_role_model
try:
    import unittest.mock as mock
except ImportError:
    import mock

FIXTURE = FIXTURE_PATH / "testing_fixture.json"
from tests.fixture import model_fixture

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsAuthorizerBackend(TransactionTestCase):
    """"""
    fixtures = (FIXTURE, )

    def setUp(self):
        """"""
        super(TestHacsAuthorizerBackend, self).setUp()
        model_fixture.init_data()
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]

    @mock.patch('hacs.security.helpers.get_user_permissions', return_value=None)
    @mock.patch('hacs.security.helpers.get_group_permissions', return_value=None)
    def test_get_group_permissions(self, mock_get_user_permissions, mock_get_group_permissions):
        """
        :param mock_get_user_permissions:
        :param mock_get_group_permissions:
        :return:
        @TODO: mock test should be done, to check if  get_user_permissions or get_group_permissions is not called
        after cache is created
        """
        backend = HacsAuthorizerBackend()
        superuser = backend.user_cls.objects.filter(is_superuser=True).first()

        administrators_group = backend.group_cls.objects.get_by_natural_key('Administrators')
        contributors_group = backend.group_cls.objects.get_by_natural_key('Contributors')
        group_cache_key = get_cache_key(backend.group_cls.__hacs_base_content_type__, administrators_group)

        # Make sure no value in cache
        self.assertIsNone(self.cache.get(administrators_group))

        permissions = backend.get_group_permissions(superuser)

        # Super User have all permissions
        self.assertEqual(len(permissions), HacsPermissionModel.objects.count())

        # Make cache is updated
        self.assertIsNotNone(self.cache.get(group_cache_key))
        self.cache.clear()

        # Make sure no value in cache
        self.assertIsNone(self.cache.get(administrators_group))

        permissions = backend.get_group_permissions(administrators_group)
        # Administrators Group have all permissions
        self.assertEqual(len(permissions), HacsPermissionModel.objects.count())
        # Make cache is updated
        self.assertIsNotNone(self.cache.get(group_cache_key))

        permissions = backend.get_group_permissions(contributors_group)
        # should have six: ('hacs.PublicView', 'hacs.AuthenticatedView', 'hacs.ViewContent', 'hacs.AddContent',
        # 'hacs.CanListObjects', 'hacs.CanTraverseContainer')
        self.assertEqual(6, len(permissions))
        # Cache Key with natural key
        group_cache_key = get_cache_key(
            backend.group_cls.__hacs_base_content_type__,
            klass=backend.group_cls.__name__,
            _id=contributors_group.name)
        self.assertIsNotNone(self.cache.get(group_cache_key))
        # Symbolic User ContentType
        permissions = backend.get_group_permissions(AnonymousUser())
        # Should Have no permission as anonymous user has no group
        self.assertEqual(0, len(permissions))

    def test_get_all_permissions(self):
        """
        :return:
        """
        backend = HacsAuthorizerBackend()
        anonymous_cache_key = get_cache_key(backend.user_cls.__hacs_base_content_type__, AnonymousUser())

        permissions = backend.get_all_permissions(AnonymousUser())
        # Anonymous User should have one permission
        self.assertEqual(1, len(permissions))
        self.assertIsNotNone(self.cache.get(anonymous_cache_key))

        normaluser = get_user_model().objects.get_by_natural_key("member@test.com")
        cache_key = get_cache_key(backend.user_cls.__hacs_base_content_type__, normaluser)
        permissions = backend.get_all_permissions(normaluser)

        # should be three ()
        self.assertEqual(3, len(permissions))
        self.assertIsNotNone(self.cache.get(cache_key))

        superuser = get_user_model().objects.filter(is_superuser=True).first()
        cache_key = get_cache_key(backend.user_cls.__hacs_base_content_type__, superuser)
        permissions = backend.get_all_permissions(superuser)
        # super user should have all permission
        self.assertEqual(len(HacsPermissionModel.objects.all()), len(permissions))

        # Test with local_roles and object
        news_item_1 = model_fixture.models.get('news_item_cls').objects.get_by_natural_key('news-one')
        news_item_2 = model_fixture.models.get('news_item_cls').\
            objects.get_by_natural_key('news-two-with-local-roles')
        contributor1 = model_fixture.contributoruser
        contributor2 = get_user_model().objects.get_by_natural_key('contributor2@test.com')
        # First `Contributor` user who has local roles for `news_item_2`
        permissions  = backend.get_all_permissions(contributor1)
        permissions1 = backend.get_all_permissions(contributor1, news_item_1)
        permissions2 = backend.get_all_permissions(contributor1, news_item_2)

        # Second `Contributor User` that has no local_roles each object
        permissions3 = backend.get_all_permissions(contributor2, news_item_1)
        permissions4 = backend.get_all_permissions(contributor2, news_item_2)

        # Editor permission without obj (although will be same with `news_item_2`)
        permissions5 = backend.get_all_permissions(get_user_model().objects.get_by_natural_key('editor@test.com'))

        # Should same number of permissions of Editor(`permissions5`) and First Contributor with `news_item_2`
        # (as local role `Editor` assigned in this object)
        self.assertEqual(len(permissions2), len(permissions5))
        # For `news_item_1` object first `Contributor` should have normal permissions for any Contributor
        self.assertEqual(len(permissions), len(permissions1))

        # Second Contributor user should also normal permissions
        self.assertEqual(len(permissions), len(permissions3))
        # Second Contributor user also should have normal permissions for `news_item_2` as no local role for
        # this user!
        self.assertEqual(len(permissions3), len(permissions4))

    def test_get_role_permissions(self):
        """
        :return:
        """
        backend = HacsAuthorizerBackend()
        # Test Manager role with object
        manager = get_role_model().objects.get_by_natural_key('Manager')
        manager_cache_key = get_cache_key(manager.__hacs_base_content_type__, manager)
        permissions = backend.get_role_permissions(manager)
        # should have all permissions
        self.assertEqual(len(HacsPermissionModel.objects.all()), len(permissions))
        self.assertIsNotNone(self.cache.get(manager_cache_key))

        # Test Guest Role with natural key
        guest_cache_key = get_cache_key(get_role_model().__hacs_base_content_type__, klass=get_role_model().__name__, _id='Guest')
        permissions = backend.get_role_permissions('Guest')
        self.assertEqual(1, len(permissions))
        self.assertEqual(1, len(self.cache.get(guest_cache_key)['permissions']))

    @mock.patch('hacs.security.helpers.get_role_permissions', return_value=None)
    def test_get_roles_permissions(self, role_permissions_fn):
        """
        :param role_permissions_fn
        :return:
        """
        backend = HacsAuthorizerBackend()
        role_cls = get_role_model()
        # Test by Using natural key
        cache_key1 = get_cache_key(role_cls.__hacs_base_content_type__, klass=role_cls.__name__,
                                  _id=hash(('Guest', 'Manager')))
        permissions = backend.get_roles_permissions('Guest', 'Manager')
        self.assertEqual(HacsPermissionModel.objects.count(), len(permissions))

        self.assertEqual(HacsPermissionModel.objects.count(), len(self.cache.get(cache_key1)))

        # Test by Using instance
        cache_key2 = get_cache_key(
            role_cls.__hacs_base_content_type__,
            klass=role_cls.__name__,
            _id=hash((role_cls.objects.get_by_natural_key('Guest'), role_cls.objects.get_by_natural_key('Manager'))))

        self.assertNotEqual(cache_key1, cache_key2)

        permissions = backend.get_roles_permissions(role_cls.objects.get_by_natural_key('Guest'), role_cls.objects.get_by_natural_key('Manager'))
        self.assertEqual(HacsPermissionModel.objects.count(), len(permissions))
        self.assertEqual(HacsPermissionModel.objects.count(), len(self.cache.get(cache_key2)))

        # Test Mix with natural key and instance
        cache_key3 = get_cache_key(
            role_cls.__hacs_base_content_type__,
            klass=role_cls.__name__, _id=hash(('Guest', role_cls.objects.get_by_natural_key('Manager'))))
        permissions = backend.get_roles_permissions('Guest', role_cls.objects.get_by_natural_key('Manager'))
        self.assertEqual(HacsPermissionModel.objects.count(), len(permissions))
        self.assertEqual(HacsPermissionModel.objects.count(), len(self.cache.get(cache_key3)))

    def tearDown(self):
        """
        :return:
        """
        model_fixture.tear_down()
        super(TestHacsAuthorizerBackend, self).tearDown()
