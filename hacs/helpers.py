# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 10/26/16 6:25 PM ++
from __future__ import unicode_literals
from django.utils import lru_cache
from django.apps import apps as global_apps
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model

from .globals import HACS_APP_NAME

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


Empty = object()


class LazyUserModelLoad(SimpleLazyObject):
    """
    """
    def __call__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        if self._wrapped is Empty:
            self._setup()
        # AS wrapped is nothing but Class so class could be initialized
        return self._wrapped(*args, **kwargs)


user_model_lazy = LazyUserModelLoad(get_user_model)


@lru_cache.lru_cache(maxsize=None)
def get_hacs_model(model_name):
    """
    :param model_name:
    :return:
    """
    model_map = {
        'role': "HacsRoleModel",
        'group': "HacsGroupModel",
        'permission': "HacsPermissionModel",
        'workflow': "HacsWorkflowModel"
    }
    try:
        return global_apps.get_model(HACS_APP_NAME, model_name)
    except LookupError:
        if model_name in model_map.keys():
            return global_apps.get_model(HACS_APP_NAME, model_map.get(model_name))
        raise


def get_group_model():
    """
    :return:
    """
    return get_hacs_model('HacsGroupModel')


def get_role_model():
    """
    :return:
    """
    return get_hacs_model('HacsRoleModel')


def get_permission_model():
    """
    :return:
    """
    return get_hacs_model('HacsPermissionModel')


def get_workflow_model():
    """
    :return:
    """
    return get_hacs_model('HacsWorkflowModel')


def get_contenttype_model():
    """
    :return:
    """
    return get_hacs_model('HacsContentType')

__all__ = [str(x) for x in (
    "user_model_lazy",
    "get_permission_model",
    "get_role_model",
    "get_group_model",
    "get_group_model",
    "get_workflow_model",
    "get_contenttype_model"
)]

