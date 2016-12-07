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
        return self._check_object(obj, action)

    def check_obj_permission(self, obj, action=None):
        """
        :param obj:
        :param action:
        :return:
        """
        # @TODO: required to make meaningful debug message
        if not self._check_object(obj, action):
            # @TODO: more meaning full message
            raise PermissionDenied

    def check_model_permission(self, model, action):
        """
        :param model:
        :param action:
        :return:
        """
        # hacs_ct = self.content_type_cls.objects.get_for_model(model)
        # # get cache key
        # key = get_content_type_key(hacs_ct.content_type, suffix='permission')
        # self.cache.get(key)

    def has_model_permission(self, model, action):
        """
        :param model:
        :param action:
        :return:
        """

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
                # which backend is complience with HACS standard
                continue
            if hasattr(backend, 'get_all_permissions'):
                user_permissions = user_permissions.union(getattr(backend, 'get_all_permissions')(user, obj))

        return len(user_permissions.intersection(permissions)) > 0

    def _check_model(self, action, model=None, container=None, raise_exception=False):
        """
        :param action:
        :param raise_exception:
        :return:
        Cache Key Format:
            1. Model Permission: {app namespace}.sm.{model ID}.{action}
            2. User Permission: {app namespace}.sm.{user ID}.permissions
            2. Container Permission: {app namespace}.sm.container.{user ID}.permissions
        """
        model = model or self.model
        assert action == 'object.create' and container is not None and getattr(model, '__hacs_base_content_type__', None) == HACS_CONTENT_TYPE_CONTENT, ""

        content_type = self.content_type_cls.objects.get_for_model(model)

    def _check_object(self, obj, action=None):
        """
        :param obj:
        :return:
        """
        base_type = getattr(obj, '__hacs_base_content_type__', None)
        if base_type is None:
            warnings.warn("Hacs Security ignored as %s is not under any Hacs Base model" % obj.__class__.__name__, UserWarning)
            return True

        if base_type in (HACS_CONTENT_TYPE_CONTAINER, HACS_CONTENT_TYPE_CONTENT):
            assert action is not None, "Action is required for %s, %s type Model"
            parent_obj = base_type == HACS_CONTENT_TYPE_CONTAINER and getattr(obj, 'parent_container_object', None) or\
                         getattr(obj, 'container_object', None)

            if parent_obj:
                if not self._check(parent_obj.permissions_actions_map['list.traverse'], parent_obj):
                    warnings.warn("Any action denied! because user don't have hacs.CanTraverseContainer parent "
                                    "container ")
                    return False

            obj_permissions = obj.permissions_actions_map[action]

        elif base_type in (HACS_CONTENT_TYPE_UTILS, HACS_CONTENT_TYPE_STATIC):
            # @TODO: may be should use cache or list of permissions string
            obj_permissions = [x.name for x in obj.permissions.all()]

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
        from django.apps import apps
        return apps.get_registered_model(HACS_APP_LABEL, "HacsContentType")
