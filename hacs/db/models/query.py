# -*- coding: utf-8 -*-
# ++ This file `query.py` is generated at 10/24/16 6:16 PM ++
import logging
from django.db.models import Q
from hacs.db.models.functions import JsonbExtractPath
from hacs.db.models.functions import JsonbToArray
from django.conf import settings
from django.db.models.query import QuerySet
from hacs.security.helpers import HACS_STATIC_CONTENT_PERMISSION
from hacs.security import SecurityManager
from hacs.defaults import HACS_AC_BYPASS
from hacs.globals import HACS_CONTENT_TYPE_USER
from hacs.globals import HACS_CONTENT_TYPE_UTILS
from hacs.globals import HACS_CONTENT_TYPE_STATIC
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger("hacs.db.model.HacsQuerySet")

__all__ = [str(x) for x in ("HacsQuerySet", "HacsBaseQuerySet", )]


class HacsBaseQuerySet(QuerySet):
    """"
    Not sure if need until now! if need anything special
    """""
    _hacs_security_manager = None
    _disable_security_guard = False
    _hacs_security_guard_applied = False

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
        self._hacs_security_guard_applied = False
        super(HacsBaseQuerySet, self).__init__(model, query, using, hints)

    def update(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        active_security_guard, current_user, base_type = self._extract_security_info()
        if active_security_guard and self.query.can_filter():
            # Yep! security guard applicable
            # self._add_security_guard(base_type, current_user, 'object.update')
            pass

        return super(HacsBaseQuerySet, self).update(**kwargs)

    update.alters_data = True

    def delete(self):
        """
        :return:
        """
        active_security_guard, current_user, base_type = self._extract_security_info()
        if active_security_guard and self.query.can_filter() and self._fields is None:
            # Yep! security guard applicable
            # self._add_security_guard(base_type, current_user, 'object.delete')
            pass

        return super(HacsBaseQuerySet, self).delete()

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

    def _clone(self, **kwargs):
        """
         Overridden private method
        :param kwargs:
        :return:
        """
        clone = super(HacsBaseQuerySet, self)._clone(**kwargs)
        clone._hacs_security_manager = self._hacs_security_manager
        clone._disable_security_guard = self._disable_security_guard
        clone._hacs_security_guard_applied = self._hacs_security_guard_applied
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

    def _extract_security_info(self):
        """
        :return:
        """
        active_security_guard = not self._disable_security_guard
        current_user = self.security_manager.get_ac_user()
        base_type = getattr(self.security_manager.model, '__hacs_base_content_type__', None)
        if active_security_guard:
            # we force disable security guard
            if current_user is None:
                logging.warning("No permission is checked because of empty user!")
                active_security_guard = False
            # Although system user clearance added in _check method but performance purpose here also implemented
            elif getattr(current_user, 'is_system', False) or getattr(current_user, 'is_superuser', False):
                if settings.DEBUG:
                    logging.info("Got %s! All permission granted!" % getattr(current_user, 'is_superuser', False) and
                                 "SuperUser" or "System User")
                active_security_guard = False
            elif getattr(settings, 'HACS_AC_BYPASS', HACS_AC_BYPASS):
                active_security_guard = False

        return active_security_guard and base_type is not None, current_user, base_type

    def _add_security_guard(self, base_type, user, action=None):
        """
        :param base_type:
        :param user:
        :return:
        """
        action = action or "object.view"
        user_permissions = user.get_all_permissions()

        if base_type in (HACS_CONTENT_TYPE_CONTENT, HACS_CONTENT_TYPE_CONTAINER):
            user_name = user.is_authenticated() and getattr(user, user.USERNAME_FIELD) or user.__str__()
            query = Q(**{
                        "permissions_actions_map__%s__has_any_keys" % action: user_permissions
                    }) | \
                    Q(acquired_owners__contains=user_name) \
                    | Q(**{
                        "roles_actions_map__%s__has_any_keys" % action: JsonbToArray('local_roles__%s' % user_name)
                    })

            if user.is_authenticated():
                query = query | Q(owner=user)

            self.query.add_q(query)

        elif base_type == HACS_CONTENT_TYPE_UTILS:
             query = Q(permissions__has_any_keys=user_permissions)
             self.query.add_q(query)

        elif base_type == HACS_CONTENT_TYPE_STATIC:
            # Only Super User can see static contents
            if HACS_STATIC_CONTENT_PERMISSION not in user_permissions:
                self.query.set_empty()

        elif base_type == HACS_CONTENT_TYPE_USER:
            # @TODO: UserModel Should use Manager from Hacs
            # Until now! security guard is not applicable here! because HacsUserModel is currently using
            # django.contrib.auth's built-in manager (initial plan was we don't want to fall info query permission
            # checking loop)
            # i.e. authenticate backend needs unrestricted user query
            # ********************************************************
            # Steps to use Hacs Manager
            # 1. Make Manager from HacsBaseManager & django.auth.BaseUserManager
            # 2. Manager's `get` and or `get_by_natural_key` methods by default should be unrestricted
            pass


class HacsQuerySet(HacsBaseQuerySet):
    """ """

    # Overridden Public Methods
    def iterator(self):
        """
        :return:
        SELECT query security is only available for this class only (default manager, not base manager)
        """
        # `object.view` action security check is checking here (previously mentioned `list.view` but that should be
        # controlled in view permission level)
        # ******************************************
        # @TODO: Must consider `local_roles`! for container type object.
        # Right now local_roles things is ignored!
        # Some Options/ Brainstorming
        # 1.
        # _self = super(HacsQuerySet, self).filter(owner=user or action_permission_maps[action:permissions] in
        # (one of match) user permissions)
        # return _self.iterator()
        active_security_guard, current_user, base_type = self._extract_security_info()

        if active_security_guard and self.query.can_filter():
            # Yep! security guard applicable
            if settings.DEBUG:
                logging.debug("Security Guard is Active! start applying permission check")
            self._add_security_guard(base_type, current_user)

        return super(HacsQuerySet, self).iterator()

    def get(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        By default get method is unrestricted!
        """
        restricted = kwargs.pop('__restricted__', False)
        self._disable_security_guard = not restricted
        return super(HacsQuerySet, self).get(*args, **kwargs)

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
