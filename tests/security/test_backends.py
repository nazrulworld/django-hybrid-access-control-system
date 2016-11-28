# -*- coding: utf-8 -*-
# ++ This file `test_backends.py` is generated at 11/23/16 5:43 PM ++

import pytest
from django.conf import settings
from django.core.cache import caches
from tests.path import FIXTURE_PATH
from django.test import TestCase
from hacs.models import HacsPermissionModel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.security.helpers import get_cache_key
from hacs.security.backends import HacsAuthorizerBackend
try:
    import unittest.mock as mock
except ImportError:
    import mock

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsAuthorizerBackend(TestCase):
    """"""
    fixtures = (FIXTURE, )

    def setUp(self):
        """"""
        super(TestHacsAuthorizerBackend, self).setUp()
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
        officers_group = backend.group_cls.objects.get_by_natural_key('Officers')
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

        permissions = backend.get_group_permissions(officers_group)

        self.assertEqual(2, len(permissions))
        # Cache Key with natural key
        group_cache_key = get_cache_key(
            backend.group_cls.__hacs_base_content_type__,
            klass=backend.group_cls.__name__,
            _id=officers_group.name)
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

        normaluser = get_user_model().objects.filter(is_superuser=False).first()
        cache_key = get_cache_key(backend.user_cls.__hacs_base_content_type__, normaluser)
        permissions = backend.get_all_permissions(normaluser)

        self.assertEqual(2, len(permissions))
        self.assertIsNotNone(self.cache.get(cache_key))

        superuser = get_user_model().objects.filter(is_superuser=True).first()
        cache_key = get_cache_key(backend.user_cls.__hacs_base_content_type__, superuser)
        permissions = backend.get_all_permissions(superuser)
        # super user should have all permission
        self.assertEqual(len(HacsPermissionModel.objects.all()), len(permissions))




