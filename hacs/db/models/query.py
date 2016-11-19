# -*- coding: utf-8 -*-
# ++ This file `query.py` is generated at 10/24/16 6:16 PM ++
import logging
from django.db.models.query import QuerySet
from hacs.security import SecurityManager

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger("hacs.HacsQuerySet::")

__all__ = [str(x) for x in ("HacsQuerySet",)]


class HacsQuerySet(QuerySet):
    """

    """
    _hacs_security_manager = None

    def __init__(self, model=None, query=None, using=None, hints=None):
        """
        :param model:
        :param query:
        :param using:
        :param hints:
        """
        self._hacs_security_manager = None
        # By default
        self._disable_security_guard = False
        super(HacsQuerySet, self).__init__(model, query, using, hints)

    # Overridden Public Methods
    def iterator(self):
        """
        :return:
        """
        # @TODO: `list.view` action security check will be here
        # self.security_manager.check_model_permission(self.model, "list.view")
        # ##
        # @TODO: restricted filters will be applied.
        # 1. we will add extra filter here! we will take benefits from JSON searchable.
        # 1.1  each object should have action permission maps, so default action could be object.view. From that action
        #  we should get permissions
        # 1.2 we will get user permissions perhaps from cache
        # 1.3 keep in mind about owner role (object's owner have by default all action permission)
        #
        # Pseudocode
        # _self = super(HacsQuerySet, self).filter(owner=user or action_permission_maps[action:permissions] in
        # (one of match) user permissions)
        # return _self.iterator()
        logging.info("Got Query Request.")

        return super(HacsQuerySet, self).iterator()

    def update(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        # @TODO: apply security guard: action = list.update
        return super(HacsQuerySet, self).update(**kwargs)

    update.alters_data = True

    def delete(self):
        """
        :return:
        """
        # @TODO: security guard here: action = list.delete
        return super(HacsQuerySet, self).delete()

    delete.alters_data = True
    delete.queryset_only = True

    def unrestricted(self):
        """
        Disable security guard:
        :return:
        """
        self._disable_security_guard = True
        return self._clone()

    @property
    def security_manager(self):
        """
        :return:
        """
        return self._security_manager()

    # Overridden Private Methods
    def _update(self, values):
        """
        :param values:
        :return:
        """
        # @TODO: Security Guard Here: This method is called from Model
        # here is one of the challenge to get object.
        # might need self.query.clone or use self._fetchall()

        return super(HacsQuerySet, self)._update(values)

    _update.alters_data = True
    _update.queryset_only = False

    def _insert(self, objs, fields, return_id=False, raw=False, using=None):
        """
        :param objs:
        :param fields:
        :param return_id:
        :param raw:
        :param using:
        :return:
        """
        # @TODO:Security Guard here:
        # a signal could be created, that will update state, permissions after save or before save.
        # Check Level: from parent if this object is allowed to insert inside that parent
        # if this object is globally allowed to insert
        # if certain user has object.create permission at ContentType
        return super(HacsQuerySet, self)._insert(objs, fields, return_id, raw, using)

    _insert.alters_data = True
    _insert.queryset_only = False

    def _clone(self, **kwargs):
        """
         Overridden private method
        :param kwargs:
        :return:
        """
        clone = super(HacsQuerySet, self)._clone(**kwargs)
        clone._hacs_security_manager = self._hacs_security_manager
        clone._disable_security_guard = self._disable_security_guard
        return clone

    def _security_manager(self):
        """
        Shared Security Manager over Manager
        :return:
        """
        if self._hacs_security_manager is None:
            self._hacs_security_manager = SecurityManager(model=self.model)

        return self._hacs_security_manager

    _security_manager.queryset_only = False



