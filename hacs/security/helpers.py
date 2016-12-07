# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 11/5/16 3:31 PM ++
from django.utils import six
from collections import deque
from collections import defaultdict
from django.conf import settings
from django.utils import lru_cache
from django.contrib.auth import get_permission_codename
from hacs.globals import HACS_APP_NAME
from hacs.defaults import HACS_ANONYMOUS_ROLE_NAME
from django.apps import apps as global_apps
from hacs.helpers import get_role_model

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

CACHE_KEY_FORMAT = "{prefix}.sm.{content_type}.{key}"
STANDARD_PERMISSIONS = {
    "hacs.PublicView": {
        "title": "Public View",
        "description": "viewable for all user including guest user!"
    },
    "hacs.AuthenticatedView": {
        "title": "Authenticated View",
        "description": "something like public view except guest user."
    },
    "hacs.ManagePortal": {
        "title": "Manage Portal"
    },
    "hacs.ManageSystem": {
        "title": "Manage System",
        "description": "something like god mode, all object by default will have this permission"
    },
    "hacs.ManageUser": {
        "title": "Manager User"
    },
    "hacs.CanIntrospect": {
        "title": "Can Introspect"
    },
    "hacs.ViewContent": {

    },
    "hacs.AddContent": {

    },
    "hacs.ModifyContent":
    {

    },
    "hacs.DeleteContent":
    {

    },
    "hacs.ManageStaticContent": {

    },
    "hacs.ManageUtilsContent": {

    },
    "hacs.CanListObjects": {

    },
    "hacs.CanModifyObjects": {

    },
    "hacs.CanDeleteObjects": {

    },
    "hacs.CanTraverseContainer": {}

}


@lru_cache.lru_cache(maxsize=1024)
def get_cache_key(content_type, content_object=None, klass=None, _id=None):
    """
    :param content_type: base type of content
    i.e user, container, content, utility
    :param content_object
    :param klass
    :param _id
    :return:
    """
    klass = klass or content_object.__class__.__name__
    if _id is None:
        try:
            _id = '.'.join(content_object.natural_key())
        except AttributeError:
            _id = content_object.pk

    return CACHE_KEY_FORMAT.format(
        prefix=HACS_APP_NAME,
        content_type=content_type,
        key="%s.%s" % (klass, _id))


def normalize_role(container, role):
    """
    :param container: must be instance of set
    :param role:
    :return:
    """
    container.add(role)
    if role.parent is not None:
        normalize_role(container, role.parent)


def get_user_permissions(user):
    """
    :param user:
    :return:
    """
    # @TODO: need to something for special users. i.e system, anonymous
    permissions = set()
    for role in get_user_roles(user, True):
        for permission in role.hacs_rlm_permissions.all():
            permissions.add(permission)

    return permissions


def get_group_permissions(group):
    """
    :param group:
    :return:
    """
    permissions = set()

    roles = set()
    for role in group.roles.all():
        normalize_role(roles, role)

    for role in roles:
        for permission in role.hacs_rlm_permissions.all():
            permissions.add(permission)

    return permissions


@lru_cache.lru_cache(maxsize=None)
def get_anonymous_user_role():
    """
    :return:
    """
    role_cls = global_apps.get_model(HACS_APP_NAME, 'HacsRoleModel')
    try:
        return role_cls.objects.get_by_natural_key(getattr(settings, 'HACS_ANONYMOUS_ROLE_NAME',
                                                           HACS_ANONYMOUS_ROLE_NAME))
    except role_cls.DoesNotExists:
        raise


def get_user_roles(user, normalized=False):
    """
    :param user:
    :param normalized: if true parent roles also me extracted
    :return:
    """
    # @TODO: need to something for special users. i.e system, anonymous
    roles = set()

    if user.is_anonymous:
        roles.add(get_anonymous_user_role())
        return roles

    for role in user.roles.all():

        if normalized:
            normalize_role(roles, role)
        else:
            roles.add(role)

    for group in user.groups.all().prefetch_related('roles'):

        for role in group.roles.all():
            if normalized:
                normalize_role(roles, role)
            else:
                roles.add(role)

    return roles


def get_container_permissions(content_type_cls, container):
    """
    :param content_type_cls:
    :param container:
    :return:
    """


@lru_cache.lru_cache(maxsize=None)
def get_django_builtin_permissions():
    """
    These permissions are used by Django Admin it-self as well
    :return:
    """
    permissions = set()

    for model in global_apps.get_models():
        opts = model._meta

        for action in opts.default_permissions:
            permissions.add("%s.%s" % (opts.app_label, get_permission_codename(action, opts)))

    return permissions


def get_django_custom_permissions():
    """
    1. These permissions could be mentioned at Model Meta.
    2. No cache, should be inserted into DB
    :return:
    """
    permissions = set()

    for model in global_apps.get_models():
        opts = model._meta
        for codename in opts.permissions:
            # @TODO: Need to define Format of permissions
            permissions.add("%s.%s" % (opts.app_label, codename))

    return permissions


def get_role_permissions(role):
    """
    :param role: string(natural key value) or instance of HacsRoleModel
    :return: list of HacsPermissionModel
    """
    role_cls = get_role_model()

    if isinstance(role, six.string_types):
        role = role_cls.objects.get_by_natural_key(role)

    if not isinstance(role, role_cls):
        raise ValueError("%s must be instance of %s class" % (role, role_cls.__name__))

    roles = set()
    normalize_role(roles, role)

    permissions = set()

    for role in roles:
        for permission in role.hacs_rlm_permissions.all():
            permissions.add(permission)

    return permissions

