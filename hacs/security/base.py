# -*- coding: utf-8 -*-
# ++ This file `base.py` is generated at 10/24/16 6:21 PM ++
import os
import logging
import warnings
from django.utils import six
from django.conf import settings
from django.core.cache import caches
from django.utils.functional import cached_property
from django.contrib.auth import get_backends
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from hacs.globals import HACS_APP_LABEL
from hacs.defaults import HACS_AC_BYPASS

from hacs.globals import HACS_CONTENT_TYPE_UTILS
from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER
from hacs.globals import HACS_CONTENT_TYPE_USER
from hacs.globals import HACS_CONTENT_TYPE_STATIC
from .backends import HacsAuthorizerBackend
from .helpers import HACS_STATIC_CONTENT_PERMISSION
from .helpers import HACS_PORTAL_MANAGER_PERMISSION
from .helpers import HacsSecurityException
# from hacs.lru_wrapped import get_content_type_key

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logging.captureWarnings(True)
logger = logging.getLogger("hacs.security::SecurityManager")


class SecurityManager(object):
    """
    """

    def __init__(self, model=None):
        """
        :param model:
        """
        self.model = model
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]

    def check_view_permission(self, permissions, view=None, request=None):
        """
        :param permissions:
        :param view
        :param request
        :return:
        """
        # @TODO: view and request are required to make meaningful debug message
        if not self._check(permissions):
            # @TODO: more meaning full message
            raise PermissionDenied

    def has_view_permission(self, permissions):
        """
        :param permissions:
        :return:
        """
        return self._check(permissions)

    def has_obj_permission(self, obj, action=None):
        """
        :param obj:
        :param action
        :return:
        """
        try:
            return self._check_object(obj, action)
        except HacsSecurityException as exc:
            logging.info(str(exc))
            return False

    def check_obj_permission(self, obj, action=None):
        """
        :param obj:
        :param action:
        :return:
        """
        # @TODO: required to make meaningful debug message
        try:
            if not self._check_object(obj, action):
                # @TODO: more meaning full message
                raise PermissionDenied
        except HacsSecurityException as exc:
            raise PermissionDenied(exc)

    def has_owner_privilege(self, obj, user=None):
        """
        :param obj:
        :param user:
        :return:
        """
        assert getattr(obj, '__hacs_base_content_type__', None) in \
               (HACS_CONTENT_TYPE_CONTAINER, HACS_CONTENT_TYPE_CONTENT), \
            "Only HACS content or container type model accepted!"

        current_user = user or self.get_ac_user()
        if current_user.is_anonymous:
            return False

        if getattr(current_user, 'is_system', False):
            # System User Has All!
            return True

        if current_user != obj.owner:
            # Let's Try From Acquired
            acquired_owners = obj.acquired_owners or []
            if getattr(current_user, current_user.USERNAME_FIELD, None) not in acquired_owners:
                return False

        return True

    def get_ac_user(self):
        """
        :return:
        """
        # @TODO: More condition should be added
        if getattr(settings, 'HACS_AC_BYPASS', HACS_AC_BYPASS) or \
                    os.environ.get('HACS_AC_BYPASS', None) in (1, '1', 'True'):
            logging.info("Hacs Security feature is disabled due to allow bypass from settings")
            return
        # If Not user is added by Middleware should be None,
        user = getattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user', None)
        if user is None:
            warnings.warn("Make sure `hacs.middleware.AccessControlMiddleware` is enabled! Hacs Security feature "
                            "is ignored as no user found!", UserWarning)
        return user

    def _check(self, permissions, obj=None):
        """
        :param permissions:
        :param obj:
        :return:
        """
        user = self.get_ac_user()
        if user is None:
            warnings.warn("No permission is checked because of empty user!", UserWarning)
            return True
        elif getattr(user, 'is_system', False):
            logging.info("Got System User! All permission granted!")
            return True

        if isinstance(permissions, six.string_types):
            permissions = (permissions, )
        if isinstance(permissions, (tuple, list)):
            permissions = set(permissions)

        user_permissions = set()
        for backend in get_backends():
            if not isinstance(backend, HacsAuthorizerBackend):
                # @TODO: for we are accepting only HacsAuthorizerBackend, but will accept all later
                # which backend is compliance with HACS standard
                continue
            if hasattr(backend, 'get_all_permissions'):
                user_permissions = user_permissions.union(getattr(backend, 'get_all_permissions')(user, obj))

        return len(user_permissions.intersection(permissions)) > 0

    def _check_object(self, obj, action=None):
        """
        :param obj:
        :return:
        """
        current_user = self.get_ac_user()
        if current_user is None:
            warnings.warn("No permission is checked because of empty user!", UserWarning)
            return True
        # Although system user clearance added in _check method but performance purpose here also implemented
        if getattr(current_user, 'is_system', False):
            logging.info("Got System User! All permission granted!")
            return True

        base_type = getattr(obj, '__hacs_base_content_type__', None)
        if base_type is None:
            warnings.warn("Hacs Security ignored as %s is not under any Hacs Base model" % obj.__class__.__name__,
                          UserWarning)
            return True

        if base_type in (HACS_CONTENT_TYPE_CONTAINER, HACS_CONTENT_TYPE_CONTENT):
            assert action is not None, "Action is required for %s, %s type Model"
            container_obj = base_type == HACS_CONTENT_TYPE_CONTAINER and getattr(obj, 'parent_container_object', None) or\
                         getattr(obj, 'container_object', None)

            # Respect ownership! only case of authenticated user and no system of course
            if action == "object.create" and container_obj:
                has_owner_priv = self.has_owner_privilege(container_obj, current_user)
            else:
                has_owner_priv = self.has_owner_privilege(obj, current_user)

            if has_owner_priv:
                logging.info("Got Ownership Privilege! All permission granted!")
                return True

            if container_obj:
                if not self._check(container_obj.permissions_actions_map['list.traverse'], container_obj):
                    warnings.warn("Any action denied! because user don't have hacs.CanTraverseContainer parent "
                                    "container ")
                    return False
            if action == "object.create":
                object_ct = self.content_type_cls.objects.get_for_model(obj.__class__)
                # controversal steps  start #
                # @TODO: because of performance issue, constraint might be handled by validators
                if not object_ct.globally_allowed and container_obj is None:
                    raise HacsSecurityException("", 9901)

                if container_obj:
                    container_ct = self.content_type_cls.objects.get_for_model(container_obj.__class__)
                    if object_ct.content_type not in container_ct.allowed_content_types.all():
                        raise HacsSecurityException("", 9902)
                # controversal steps  end #
                # Only `object.create`\s permission comes from content type
                obj_permissions = object_ct.permissions_actions_map[action]
                # We pass object/instance value None for object creation action!
                # Local roles should not have any impact, in other words local roles invalid during creation
                # But if has container/parent and it has local roles, should try ofcourse
                return self._check(obj_permissions, container_obj and container_obj.recursive and container_obj or None)
            else:
                obj_permissions = obj.permissions_actions_map[action]

        elif base_type == HACS_CONTENT_TYPE_UTILS:
            # @TODO: may be should use cache or list of permissions string
            obj_permissions = obj.permissions
        elif base_type == HACS_CONTENT_TYPE_STATIC:
            obj_permissions = HACS_STATIC_CONTENT_PERMISSION

        elif base_type == HACS_CONTENT_TYPE_USER:
            # @TODO: Need to plan, what should be
            obj_permissions = "hacs.ManageUser"
        else:
            # Default Must Be Super User
            obj_permissions = HACS_PORTAL_MANAGER_PERMISSION

        return self._check(obj_permissions, obj)

    @classmethod
    def using_model(cls, model):
        """
        :param model:
        :return:
        """
        return cls(model)

    @cached_property
    def content_type_cls(self):
        """
        :return: hacs.models.HacsContentType
        """
        from hacs.helpers import get_contenttype_model
        return get_contenttype_model()
