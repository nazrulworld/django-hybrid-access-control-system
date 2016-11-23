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

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHelpers(TestCase):

    fixtures = (FIXTURE, )

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

        normaluser = user_cls.objects.filter(is_superuser=False).first()
        # Role chain: Guest -> Member -> Contributor
        roles = get_user_roles(normaluser, True)
        self.assertEqual(3, len(roles))

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

        normaluser = user_cls.objects.filter(is_superuser=False).first()
        permissions = get_user_permissions(normaluser)

        # Should have two permissions
        self.assertEqual(2, len(permissions))

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

        manager_group = group_cls.objects.get_by_natural_key("Managers")
        permissions = get_group_permissions(manager_group)
        # Should have two groups
        self.assertEqual(2, len(permissions))

        office_group = group_cls.objects.get_by_natural_key("Officers")
        permissions = get_group_permissions(office_group)
        # Should have also two permissions
        self.assertEqual(2, len(permissions))

