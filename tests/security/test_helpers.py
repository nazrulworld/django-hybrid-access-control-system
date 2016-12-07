# -*- coding: utf-8 -*-
# ++ This file `test_helpers.py` is generated at 11/23/16 5:42 PM ++
import pytest
from tests.path import FIXTURE_PATH
from django.test import TestCase
from django.apps import apps as global_apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from hacs.security.helpers import *
from hacs.defaults import HACS_ANONYMOUS_ROLE_NAME
from hacs.globals import HACS_CONTENT_TYPE_USER
from hacs.helpers import get_role_model
from hacs.helpers import get_permission_model

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHelpers(TestCase):

    fixtures = (FIXTURE, )

    def test_get_cache_key(self):
        """
        :return:
        """
        # Logically AnonymousUser contains same as UserModel
        anonymouse_user_key = get_cache_key(get_user_model().__hacs_base_content_type__, AnonymousUser())
        self.assertEqual(CACHE_KEY_FORMAT.format(prefix="hacs", content_type=HACS_CONTENT_TYPE_USER, key='AnonymousUser.None'), anonymouse_user_key)
        # Get Cache Key using object
        superuser = get_user_model().objects.get_by_natural_key("superuser@test.com")
        superuser_cache_key = get_cache_key(get_user_model().__hacs_base_content_type__, superuser)
        self.assertEqual(superuser_cache_key,
                         CACHE_KEY_FORMAT.format(prefix='hacs', content_type=HACS_CONTENT_TYPE_USER,
                                                 key="%s.%s" % (get_user_model().__name__,
                                                                getattr(superuser, get_user_model().USERNAME_FIELD))))
        # Get Cache Key using natural key
        superuser_cache_key = get_cache_key(
            get_user_model().__hacs_base_content_type__,
            klass=get_user_model().__name__,
            _id=getattr(superuser, get_user_model().USERNAME_FIELD))

        self.assertEqual(superuser_cache_key,
                         CACHE_KEY_FORMAT.format(prefix='hacs', content_type=HACS_CONTENT_TYPE_USER,
                                                 key="%s.%s" % (get_user_model().__name__,
                                                                getattr(superuser, get_user_model().USERNAME_FIELD))))

    def test_get_django_custom_permissions(self):
        """
        :return:
        """
        permissions = get_django_custom_permissions()
        # Should be zero as no custom permissions assianed yet at any model
        self.assertEqual(0, len(permissions))

    def test_get_django_builtin_permissions(self):
        """
        :return:
        """
        permissions = get_django_builtin_permissions()
        number_of_models = len(global_apps.get_models())
        # Each model should have 3 actions
        self.assertEqual(number_of_models * 3, len(permissions))

    def test_get_anonymous_user_role(self):
        """
        :return:
        """
        role = get_anonymous_user_role()
        from hacs.defaults import HACS_ANONYMOUS_ROLE_NAME
        self.assertEqual(HACS_ANONYMOUS_ROLE_NAME, role.name)

    def test_get_user_roles(self):
        """
        :return:
        """
        user_cls = get_user_model()
        superuser = user_cls.objects.filter(is_superuser=True).first()
        # Should be 5 roles after normalization.
        # Role chain: Guest -> Member -> Contributor -> Editor -> Manager
        roles = get_user_roles(superuser, normalized=True)
        self.assertEqual(5, len(roles))

        roles = get_user_roles(superuser, False)
        # Should be 1 role, because normalization set to false
        self.assertEqual(1, len(roles))

        normaluser = user_cls.objects.get_by_natural_key("member@test.com")
        # Role chain: Guest -> Member
        roles = get_user_roles(normaluser, True)
        self.assertEqual(2, len(roles))

        # Anonymous User
        anonuser = AnonymousUser()
        roles = get_user_roles(anonuser, True)
        # Only One Role
        self.assertEqual(1, len(roles))

        # Should be `Guest` role
        self.assertEqual(HACS_ANONYMOUS_ROLE_NAME, list(roles)[0].name)

    def test_get_user_permissions(self):
        """
        :return:
        """
        user_cls = get_user_model()
        superuser = user_cls.objects.filter(is_superuser=True).first()

        permissions = get_user_permissions(superuser)

        permission_cls = global_apps.get_model(HACS_APP_NAME, 'HacsPermissionModel')
        all_permissions = permission_cls.objects.all()

        # Should have all permissions
        self.assertEqual(len(permissions), all_permissions.count())

        normaluser = user_cls.objects.get_by_natural_key("member@test.com")
        permissions = get_user_permissions(normaluser)

        # Should have three permissions
        self.assertEqual(3, len(permissions))

        permissions = get_user_permissions(AnonymousUser())
        # Should have only one permission
        self.assertEqual(1, len(permissions))

    def test_get_group_permissions(self):
        """
        :return:
        """
        group_cls = global_apps.get_model(HACS_APP_NAME, 'HacsGroupModel')

        admin_group = group_cls.objects.get_by_natural_key("Administrators")
        permissions = get_group_permissions(admin_group)
        permission_cls = global_apps.get_model(HACS_APP_NAME, 'HacsPermissionModel')
        all_permissions = permission_cls.objects.all()
        # Like SuperUser, should have all permissions
        self.assertEqual(len(permissions), all_permissions.count())

        editor_group = group_cls.objects.get_by_natural_key("Editors")
        permissions = get_group_permissions(editor_group)
        # Should have should have ten permissions
        self.assertEqual(10, len(permissions))

        contributor_group = group_cls.objects.get_by_natural_key("Contributors")
        permissions = get_group_permissions(contributor_group)
        # Should have six permissions
        self.assertEqual(6, len(permissions))


    def test_get_role_permissions(self):
        """
        :return:
        """
        # test using role natural key
        permissions = get_role_permissions('Guest')
        # Guest should have one permission
        self.assertEqual(1, len(permissions))

        # test using object
        manager_role = get_role_model().objects.get_by_natural_key('Manager')
        permissions = get_role_permissions(manager_role)

        self.assertEqual(len(get_permission_model().objects.all()), len(permissions))

