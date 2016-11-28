# -*- coding: utf-8 -*-
# ++ This file `backends.py` is generated at 11/22/16 6:05 PM ++
from collections import defaultdict
from django.conf import settings
from django.core.cache import caches
from django.apps import apps as global_apps
from django.contrib.auth.models import AnonymousUser

from hacs.helpers import get_group_model
from hacs.helpers import get_user_model
from hacs.defaults import HACS_CACHE_SETTING_NAME
from .helpers import get_cache_key
from .helpers import get_group_permissions
from .helpers import get_user_permissions
from .helpers import get_role_permissions
from .helpers import get_django_builtin_permissions



__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class HacsAuthorizerBackend(object):
    """
    """
    def __init__(self):
        """"""
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        self.group_cls = get_group_model()
        self.user_cls = get_user_model()

    def get_group_permissions(self, user_or_group, obj=None):
        """
        :param user_or_group:
        :param obj:
        :return: all permissions of a group or groups those belongs to certain user
        """
        # @TODO: Need to take care if obj is not None
        is_user = isinstance(user_or_group, self.user_cls) or isinstance(user_or_group, AnonymousUser)

        if is_user:
            permissions = set() # get_user_permissions(user_or_group)
            for group in user_or_group.groups.all():
                _permissions = self.get_group_permissions(group)
                if _permissions:
                    permissions = permissions.union(_permissions)

            return tuple(permissions)

        else:
            cache_key = get_cache_key(user_or_group.__hacs_base_content_type__, user_or_group)
            result = self.cache.get(cache_key)
            if result:
                try:
                    return result['permissions']
                except KeyError:
                    pass
            else:
                result = defaultdict()

            permissions = get_group_permissions(user_or_group)
            result['permissions'] = tuple(map(lambda x: x.name, permissions))
            self.cache.set(cache_key, result)
            return result['permissions']

    def authenticate(self, username, password):
        """ HACS is doing anything with authentication  """
        return None

    def has_perm(self, user, perm, obj=None):
        """
        :param user:
        :param perm:
        :param obj:
        :return:
        """
        # This method is required by Django Admin
        if user.is_superuser and user.is_active and perm in get_django_builtin_permissions() and obj is None:
            # Let's allow, Django Admin to be visible
            return True
        # @TODO: let's contact with Security Manager, even if super user!
        return False

    def get_all_permissions(self, user, obj=None):
        """
        All permissions assigned to a user
        :param user:
        :param obj:
        :return:
        """
        cache_key = get_cache_key(user.__hacs_base_content_type__, user)
        result = self.cache.get(cache_key)

        if result:
            try:
                return result['permissions']
            except KeyError:
                pass
        else:
            result = defaultdict()

        permissions = set()

        _permissions = get_user_permissions(user)
        if _permissions:
            permissions = permissions.union(_permissions)

        for group in user.groups.all():
            _permissions = get_group_permissions(group)
            if _permissions:
                permissions = permissions.union(_permissions)

        result['permissions'] = map(lambda x: x.name, permissions)
        self.cache.set(cache_key, result)
        return result['permissions']

    def has_module_perms(self, user, app_label):
        """
        :param user:
        :param app_label:
        :return:
        """
        if user.is_superuser and user.is_active:
            for permission in get_django_builtin_permissions():
                if permission[:permission.index('.')] == app_label:
                    return True

        # TODO: Need to attached with Security Manager, for now always true
        return False

    def get_role_permissions(self, role):
        """
        :param role:
        :return:
            list all permissions those are belongs to a certain role and also permissions from parent role if
            applicable
        """
        cache_key = get_cache_key(role.__hacs_base_content_type__, role)
        result = self.cache.get(cache_key)
        if result:
            try:
                return result['permissions']
            except KeyError:
                pass
        else:
            result = defaultdict()

        result['permissions'] = tuple(get_role_permissions(role))
        self.cache.set(cache_key, result)
        return result['permissions']
