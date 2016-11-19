# -*- coding: utf-8 -*-
# ++ This file `manager.py` is generated at 10/24/16 6:20 PM ++
from hacs.db.models.query import HacsQuerySet
from django.db.models.manager import Manager, BaseManager
from django.contrib.auth.base_user import BaseUserManager


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class HacsBaseManager(BaseManager.from_queryset(HacsQuerySet)):
    """
    HACS:: Base Manager
    """


class HacsModelManager(Manager.from_queryset(HacsQuerySet)):
    """
    """

    def get_by_natural_key(self, slug):
        """
        :param slug:
        :return:
        """
        if isinstance(slug, (list, tuple)):
            slug = slug[0]
        return self.get(slug=slug)


class HacsStaticModelManager(Manager.from_queryset(HacsQuerySet)):
    """
    """

    def get_by_natural_key(self, name):
        """
        :param name:
        :return:
        """
        if isinstance(name, (list, tuple)):
            name = name[0]
        return self.get(name=name)
