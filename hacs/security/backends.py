# -*- coding: utf-8 -*-
# ++ This file `backends.py` is generated at 11/22/16 6:05 PM ++
from collections import defaultdict
from django.conf import settings
from django.core.cache import caches
from django.utils import six
from django.contrib.auth.models import AnonymousUser

from hacs.helpers import get_group_model
from hacs.helpers import get_user_model
from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from .helpers import get_cache_key
from .helpers import get_group_permissions
from .helpers import get_user_permissions
from .helpers import get_role_permissions
from .helpers import get_permission_roles
from .helpers import get_user_roles
from .helpers import get_user_cache_key
from .helpers import get_django_builtin_permissions
from hacs.helpers import get_role_model
from hacs.helpers import get_permission_model

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
            for group in user_or_group.groups.unrestricted():
                _permissions = self.get_group_permissions(group)
                if _permissions:
                    permissions = permissions.union(_permissions)

            return tuple(permissions)

        else:
            cache_key = get_cache_key(user_or_group.__hacs_base_content_type__, user_or_group)
            permissions = self.cache.get(cache_key)

            if permissions:
                return permissions

            permissions = tuple(map(lambda x: x.name, get_group_permissions(user_or_group, unrestricted=True)))
            self.cache.set(cache_key, permissions)

            return permissions

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
        local_role_permissions = set()

        if obj and getattr(obj, "__hacs_base_content_type__", None) in (HACS_CONTENT_TYPE_CONTAINER,
                                                                        HACS_CONTENT_TYPE_CONTENT):
            if obj.local_roles:
                try:
                    roles = obj.local_roles[getattr(user, user.USERNAME_FIELD)]
                    if len(roles) == 1:
                        _permissions = self.get_role_permissions(roles[0])
                    else:
                        _permissions = self.get_roles_permissions(*roles)
                    if _permissions:
                        local_role_permissions = local_role_permissions.union(_permissions)
                except KeyError:
                    pass
        # User Cache Key
        # @TODO: nice to have central method to get user cache key!
        cache_key = get_user_cache_key(user)
        # user settings could have contains other than permissions
        user_settings = self.cache.get(cache_key)

        if user_settings:
            try:
                permissions = user_settings['permissions']
                if local_role_permissions:
                    permissions = tuple(local_role_permissions.union(permissions))
                return permissions
            except KeyError:
                pass
        else:
            user_settings = defaultdict()

        permissions = set()
        _permissions = get_user_permissions(user, unrestricted=True)
        if _permissions:
            permissions = permissions.union(_permissions)

        for group in user.groups.unrestricted():
            _permissions = get_group_permissions(group, unrestricted=True)
            if _permissions:
                permissions = permissions.union(_permissions)

        permissions = user_settings['permissions'] = tuple(map(lambda x: x.name, permissions))
        self.cache.set(cache_key, user_settings)

        if local_role_permissions:
            permissions = tuple(local_role_permissions.union(permissions))

        return permissions

    def get_all_roles(self, user, obj=None):
        """
        :param user:
        :param obj:
        :return:
        """
        local_roles = set()
        if obj and getattr(obj, "__hacs_base_content_type__", None) in (HACS_CONTENT_TYPE_CONTAINER,
                                                                        HACS_CONTENT_TYPE_CONTENT):
            if obj.local_roles:
                if user.is_authenticated():
                    try:
                        local_roles = local_roles.union(obj.local_roles[getattr(user, user.USERNAME_FIELD)])
                    except KeyError:
                        pass

        cache_key = get_user_cache_key(user)
        user_settings = self.cache.get(cache_key)
        if user_settings:
            try:
                roles = user_settings['roles']
                if local_roles:
                    roles = tuple(local_roles.union(roles))
                return roles
            except KeyError:
                pass
        else:
            user_settings = defaultdict()

        # No cache! try fresh
        roles = user_settings['roles'] = tuple(map(lambda x: x.name, get_user_roles(user, normalized=True,
                                                                                    unrestricted=True)))
        self.cache.set(cache_key, user_settings)

        if local_roles:
            roles = tuple(local_roles.union(roles))
        return roles

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
        if isinstance(role, six.string_types):
            # OK role's natural key is provided
            role_cls = get_role_model()
            cache_key = get_cache_key(role_cls.__hacs_base_content_type__, klass=role_cls.__name__, _id=role)
        else:
            cache_key = get_cache_key(role.__hacs_base_content_type__, role)

        permissions = self.cache.get(cache_key)
        if permissions:
            return permissions

        permissions = tuple(map(lambda x: x.name, get_role_permissions(role, unrestricted=True)))
        self.cache.set(cache_key, permissions)
        return permissions

    def get_roles_permissions(self, *roles):
        """
        :param roles: list of natural key of HacsRoleModel or instance of HacsRoleModel
        :return:
        """
        assert len(roles) > 0, "At least one argument is required!"

        if len(roles) == 1:
            return self.get_role_permissions(roles[0])

        role_cls = get_role_model()

        cache_key = get_cache_key(role_cls.__hacs_base_content_type__, klass=role_cls.__name__, _id=hash(roles))
        permissions = self.cache.get(cache_key)

        if permissions:
            return permissions
        else:
            permissions = set()

        for role in roles:
            permissions = permissions.union(self.get_role_permissions(role))

        permissions = tuple(permissions)
        self.cache.set(cache_key, permissions)
        return permissions

    def get_permission_roles(self, permission):
        """
        :param permission:
        :return:
            list all roles those are belongs to a certain permission and
        """
        if isinstance(permission, six.string_types):
            # OK permission's natural key is provided
            permission_cls = get_permission_model()
            cache_key = get_cache_key(permission_cls.__hacs_base_content_type__,
                                      klass=permission_cls.__name__, _id=permission)
        else:
            cache_key = get_cache_key(permission.__hacs_base_content_type__, permission)

        roles = self.cache.get(cache_key)
        if roles:
            return roles

        roles = tuple(map(lambda x: x.name, get_permission_roles(permission, unrestricted=True)))
        self.cache.set(cache_key, roles)

        return roles

    def get_permissions_roles(self, *permissions):
        """
        :param permissions: list of natural key of HacsPermissionModel or instance of HacsPermissionModel
        :return:
        """
        assert len(permissions) > 0, "At least one argument is required!"
        if len(permissions) == 1:
            return self.get_permission_roles(permissions[0])

        permission_cls = get_permission_model()
        cache_key = get_cache_key(permission_cls.__hacs_base_content_type__,
                                  klass=permission_cls.__name__, _id=hash(permissions))

        roles = self.cache.get(cache_key)
        if roles:
            return roles
        else:
            roles = set()

        for permission in permissions:
            roles = roles.union(self.get_permission_roles(permission))

        roles = tuple(roles)
        self.cache.set(cache_key, roles)
        return roles
