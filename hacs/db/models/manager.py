# -*- coding: utf-8 -*-
# ++ This file `manager.py` is generated at 10/24/16 6:20 PM ++
from hacs.db.models.query import HacsQuerySet
from hacs.db.models.query import HacsBaseQuerySet
from django.db.models.manager import Manager, BaseManager
from django.contrib.auth.base_user import BaseUserManager


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class HacsBaseManager(BaseManager.from_queryset(HacsBaseQuerySet)):
    """
    HACS:: Base Manager
    """


class HacsModelManager(Manager.from_queryset(HacsQuerySet)):
    """
    """

    def get_by_natural_key(self, slug, __restricted__=False):
        """
        :param slug:
        :param __restricted__
        :return:
        """
        if isinstance(slug, (list, tuple)):
            slug = slug[0]
        params = {
            "slug": slug
        }
        if __restricted__:
            params["__restricted__"] = __restricted__

        return self.get(**params)


class HacsStaticModelManager(Manager.from_queryset(HacsQuerySet)):
    """
    """

    def get_by_natural_key(self, name, __restricted__=False):
        """
        :param name:
        :param __restricted__:
        :return:
        """
        if isinstance(name, (list, tuple)):
            name = name[0]
        params = {
            "name": name
        }
        if __restricted__:
            params["__restricted__"] = __restricted__

        return self.get(**params)
