# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 11/5/16 3:31 PM ++
from collections import deque
from collections import defaultdict
from django.utils import lru_cache
from hacs.globals import HACS_APP_NAME

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

CACHE_KEY_FORMAT = "{prefix}.sm.{content_type}.{key}"


@lru_cache.lru_cache(maxsize=1024)
def get_cache_key(content_type, content_object):
    """
    :param content_type: base type of content
    i.e user, container, content, utility
    :param content_object
    :return:
    """
    return CACHE_KEY_FORMAT.format(
        prefix=HACS_APP_NAME,
        content_type=content_type,
        key="%s.%s" % (content_type.__class__, content_object.pk))


def get_user_permissions(user):
    """
    :param user:
    :return:
    """
    # @TODO: need to something for special users. i.e system, anonymous
    permissions = deque()
    for role in user.roles.prefetch_related('hacs_rlm_role_permissions_set'):
        for permission in role.hacs_rlm_role_permissions_set:
            permissions.append(permission)

    for group in user.groups.prefetch_related('roles__hacs_rlm_role_permissions_set'):
        for role in group.roles:
            for permission in role.hacs_rlm_role_permissions_set:
                permissions.append(permission)

    return frozenset(permissions)


def get_user_roles(user):
    """
    :param user:
    :return:
    """
    # @TODO: need to something for special users. i.e system, anonymous
    roles = [role for role in user.roles.all()]

    for group in user.groups.prefetch_related('roles'):
        for role in group.roles:
            roles.append(role)

    return frozenset(roles)


def get_container_permissions(content_type_cls, container):
    """
    :param content_type_cls:
    :param container:
    :return:
    """







