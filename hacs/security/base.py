# -*- coding: utf-8 -*-
# ++ This file `base.py` is generated at 10/24/16 6:21 PM ++
import os
from django.conf import settings
from django.core.cache import caches
from django.utils.functional import cached_property
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from hacs.globals import HACS_APP_LABEL
from hacs.defaults import HACS_AC_BYPASS

from hacs.globals import HACS_CONTENT_TYPE_UTILS
from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER

# from hacs.lru_wrapped import get_content_type_key

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class SecurityManager(object):
    """
    """

    def __init__(self, model=None):
        """
        :param model:
        """
        self.model = model
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]

    def check_permission(self, user, permissions):
        """
        :param user:
        :param permissions:
        :return:
        """
    def has_permission(self, user, permissions):
        """
        :param user:
        :param permissions:
        :return:
        """

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
            # If Not user is added by Middleware should be None,
            return getattr(HACS_ACCESS_CONTROL_LOCAL, '__current_user', None)

    def _check(self, user, permissions, raise_exception=False):
        """
        :param user:
        :param permissions:
        :param raise_exception:
        :return:
        """
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



    def _check_object(self, obj, raise_exception=False):
        """
        :param obj:
        :param raise_exception:
        :return:
        """

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
