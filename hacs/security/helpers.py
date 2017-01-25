# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 11/5/16 3:31 PM ++
from django.utils import six
from django.conf import settings
from django.utils import lru_cache
from django.contrib.auth import get_backends
from django.contrib.auth.models import AnonymousUser as DAU
from django.contrib.auth import get_permission_codename
from django.utils.encoding import python_2_unicode_compatible

from hacs.globals import HACS_APP_NAME
from hacs.defaults import HACS_ANONYMOUS_ROLE_NAME
from django.apps import apps as global_apps
from hacs.helpers import get_role_model
from hacs.helpers import get_permission_model
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER

# Proxy Translation: @TODO: could be used django translation
_ = lambda x: x

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


def _user_get_all_permissions(user, obj=None):
    """
    :param user:
    :param obj:
    :return:
    """
    hacs_backend = None
    for backend in get_backends():
        if backend.__class__.__name__ == "HacsAuthorizerBackend":
            hacs_backend = backend
            break
    assert hacs_backend, "'hacs.security.backends.HacsAuthorizerBackend' is need to added in settings"

    return hacs_backend.get_all_permissions(user, obj)


def _user_get_all_roles(user, obj=None):
    """
    :param user:
    :param obj:
    :return:
    """
    hacs_backend = None
    for backend in get_backends():
        if backend.__class__.__name__ == "HacsAuthorizerBackend":
            hacs_backend = backend
            break
    assert hacs_backend, "'hacs.security.backends.HacsAuthorizerBackend' is need to added in settings"

    return hacs_backend.get_all_roles(user, obj)


class AnonymousUser(DAU):
    """
    """
    def get_all_permissions(self, obj=None):
        """
        :param obj:
        :return:
        """
        return _user_get_all_permissions(self, obj)


@python_2_unicode_compatible
class SystemUser(AnonymousUser):
    """
    """
    is_active = True

    @property
    def is_system(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm_list, obj=None):
        return True

    def has_module_perms(self, module):
        return True

    def __str__(self):

        return "SystemUser"

ANONYMOUS_USER = AnonymousUser()
SYSTEM_USER = SystemUser()
CACHE_KEY_FORMAT = "{prefix}.sm.{content_type}.{key}"
HACS_STATIC_CONTENT_PERMISSION = "hacs.ManageStaticContent"
HACS_PORTAL_MANAGER_PERMISSION = "hacs.ManagePortal"
HACS_CONTENT_ADD_PERMISSION = "hacs.AddContent"
STANDARD_PERMISSIONS = {
    "hacs.PublicView": {
        "title": "Public View",
        "description": "viewable for all user including guest user!"
    },
    "hacs.AuthenticatedView": {
        "title": "Authenticated View",
        "description": "something like public view except guest user."
    },
    HACS_PORTAL_MANAGER_PERMISSION: {
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
    "hacs.ManageContent": {},
    "hacs.ViewContent": {},
    HACS_CONTENT_ADD_PERMISSION: {},
    "hacs.ModifyContent": {},
    "hacs.DeleteContent": {},
    HACS_STATIC_CONTENT_PERMISSION: {},
    "hacs.ManageUtilsContent": {},
    "hacs.CanListObjects": {},
    "hacs.CanModifyObjects": {},
    "hacs.CanDeleteObjects": {},
    "hacs.CanTraverseContainer": {},
    "hacs.ManageLocalRole": {},
    "hacs.ManageContentState": {}

}

HACS_OBJECT_CREATE_ACTION = "object.create"
HACS_OBJECT_EDIT_ACTION = "object.edit"
HACS_OBJECT_DELETE_ACTION = "object.delete"
# Actions Definition
HACS_ACTIONS = {
    'list.traverse': {
      "title": _("List: Traverse"),
      "description": "Special action type, just like `execute` permission on directory on UNIX."
                     "This is very important action for child operation!. If"
                     "any user don't have this action permission, she cant do anything with child object even she "
                     "might have local permission"
    },
    'list.view': {
        'title': _("List: View"),
        'description': "In Django ORM sense `query`."
    },
    'list.update': {
        'title': _("List: Update"),
        'description': "In Django ORM sense `update` from QuerySet"
    },
    'list.delete': {
        'title': _("List: View"),
        'description': "In Django ORM sense `delete` from QuerySet"
    },
    'object.view': {
        'title': _("Individual Object View")
    },
    HACS_OBJECT_CREATE_ACTION : {
        'title': _("Create")
    },
    HACS_OBJECT_EDIT_ACTION: {
        'title': _("Edit")
    },
    HACS_OBJECT_DELETE_ACTION: {
        'title': _("Delete"),
    },
    'object.manage_state': {
        'title': _("Manage State"),
    },
    'share': {
        'title': "Share",
        "description": "Share means assigning Local Roles"
    },

}


class HacsSecurityException(Exception):
    """
    """
    def __init__(self, message, code=None):
        """
        :param message:
        :param code:
        """
        super(HacsSecurityException, self).__init__(code, message)
        self.code = code


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


def get_user_cache_key(user):
    """
    :param user:
    :return:
    """
    return get_cache_key(user.__hacs_base_content_type__, user)


def normalize_role(container, role):
    """
    :param container: must be instance of set
    :param role:
    :return:
    """
    container.add(role)
    if role.parent is not None:
        normalize_role(container, role.parent)


def normalize_role_children(container, role, unrestricted=False):
    """
    :param container: must be instance of set
    :param role:
    :param unrestricted:
    :return:
    """
    container.add(role)
    if unrestricted:
        query_set = role.hacs_rlm_children.unrestricted()
    else:
        query_set = role.hacs_rlm_children.all()

    for child in query_set:
        normalize_role_children(container, child, unrestricted=unrestricted)

    return container


def normalize_permission(container, permission):
    """
    :param container: must be instance of set
    :param permission:
    :return:
    """
    container.add(permission)
    if permission.parent is not None:
        normalize_role(container, permission.parent)


def get_user_permissions(user, unrestricted=False):
    """
    :param user:
    :param unrestricted:
    :return:
    """
    # @TODO: need to something for special users. i.e system
    permissions = set()
    for role in get_user_roles(user, True, unrestricted=unrestricted):
        if unrestricted:
            query_set = role.hacs_rlm_permissions.unrestricted()
        else:
            query_set = role.hacs_rlm_permissions.all()
        for permission in query_set:
            permissions.add(permission)

    return permissions


def get_group_permissions(group, unrestricted=False):
    """
    :param group:
    :param unrestricted:
    :return:
    """
    permissions = set()
    roles = set()

    if unrestricted:
        query_set = group.roles.unrestricted()
    else:
        query_set = group.roles.all()

    for role in query_set:
        normalize_role(roles, role)

    for role in roles:
        if unrestricted:
            query_set = role.hacs_rlm_permissions.unrestricted()
        else:
            query_set = role.hacs_rlm_permissions.all()

        for permission in query_set:
            permissions.add(permission)

    return permissions


@lru_cache.lru_cache(maxsize=None)
def get_anonymous_user_role():
    """
    :return:
    """
    role_cls = global_apps.get_model(HACS_APP_NAME, 'HacsRoleModel')

    try:
        return role_cls.objects.get_by_natural_key(
            getattr(settings, 'HACS_ANONYMOUS_ROLE_NAME', HACS_ANONYMOUS_ROLE_NAME)
        )
    except role_cls.DoesNotExists:
        raise


def get_user_roles(user, normalized=False, unrestricted=False):
    """
    :param user:
    :param normalized: if true parent roles also me extracted
    :param unrestricted:
    :return:
    """
    # @TODO: need to something for special users. i.e system
    roles = set()

    if user.is_anonymous:
        roles.add(get_anonymous_user_role())
        return roles
    if unrestricted:
        query_set = user.roles.unrestricted()
    else:
        query_set = user.roles.all()

    for role in query_set:

        if normalized:
            normalize_role(roles, role)
        else:
            roles.add(role)

    if unrestricted:
        query_set = user.groups.unrestricted()
    else:
        query_set = user.groups.all()

    for group in query_set.prefetch_related('roles'):

        if unrestricted:
            q_set = group.roles.unrestricted()
        else:
            q_set = group.roles.all()
        for role in q_set:
            if normalized:
                normalize_role(roles, role)
            else:
                roles.add(role)

    return roles


def get_group_roles(group, normalized=True, unrestricted=False):
    """
    :param group:
    :param normalized: if true parent roles also me extracted
    :param unrestricted:
    :return:
    """
    # @TODO: need to something for special users. i.e system
    roles = set()
    if unrestricted:
        query_set = group.roles.unrestricted()
    else:
        query_set = group.roles.all()

    for role in query_set:
        if normalized:
            normalize_role(roles, role)
        else:
            roles.add(role)
    return roles


def get_permission_roles(permission, normalized=True, unrestricted=False):
    """
    :param permission:
    :param normalized:
    :param unrestricted:
    :return:
    """
    if isinstance(permission, six.string_types):
        try:
            permission = get_permission_model().objects.get_by_natural_key(permission)
        except get_permission_model().DoesNotExist:
            # @TODO need raise with useful message
            raise

    permissions = set()
    if normalized:
        normalize_permission(permissions, permission)
    else:
        permissions.add(permission)

    container = set()
    for perm in permissions:
        if unrestricted:
            q_set = perm.roles.unrestricted()
        else:
            q_set = perm.roles.all()

        for role in q_set:
            normalize_role_children(container, role)
    return container


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


def get_role_permissions(role, unrestricted=False):
    """
    :param role: string(natural key value) or instance of HacsRoleModel
    :param unrestricted:
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
        if unrestricted:
            q_set = role.hacs_rlm_permissions.unrestricted()
        else:
            q_set = role.hacs_rlm_permissions.all()

        for permission in q_set:
            permissions.add(permission)

    return permissions


def get_container_workflow(container_obj, unrestricted=False):
    """
    :param container_obj:
    :param unrestricted:
    :return:
    """
    assert container_obj.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER, "Instance must be derived from " \
                                                                                    "HacsContainerModel"
    if container_obj.workflow:
        return container_obj.workflow


def attach_system_user():
    """
    :return:
    """
    current_user = getattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user', None)
    assert not isinstance(current_user, SystemUser), "System User is already attached!"
    assert getattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user_backup', None) is None, \
        "HACS_ACCESS_CONTROL_LOCAL.current_user_backup has as user! This is error, you might be attached system user " \
        "but forget to release system user."
    if current_user is not None:
        setattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user_backup', current_user)

    setattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user', SYSTEM_USER)


def release_system_user():
    """
    :return:
    """
    current_user = getattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user', None)
    assert isinstance(current_user, SystemUser), "System User is not attached yet!"
    backup_user = getattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user_backup', None)
    HACS_ACCESS_CONTROL_LOCAL.__release_local__()
    if backup_user is not None:
        setattr(HACS_ACCESS_CONTROL_LOCAL, 'current_user', backup_user)

