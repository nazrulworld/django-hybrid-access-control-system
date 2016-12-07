# -*- coding: utf-8 -*-
# ++ This file `base.py` is generated at 10/24/16 6:16 PM ++
from __future__ import unicode_literals
# **** Monkey Patch! enable custom HACS options at Meta class
import django.db.models.options
django.db.models.options.DEFAULT_NAMES += ('globally_allowed', 'allowed_content_types', 'hacs_default_permissions')
# ************************************************************
import uuid
import logging
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import _user_has_module_perms
from django.contrib.auth.models import _user_get_all_permissions
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from hacs.fields import DictField
from hacs.fields import ForeignKey
from hacs.fields import ManyToManyField
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_USER
from hacs.globals import HACS_CONTENT_TYPE_UTILS
from hacs.globals import HACS_CONTENT_TYPE_STATIC
from .manager import HacsBaseManager, \
    HacsModelManager, \
    HacsStaticModelManager
from .tracker import FieldTracker
from .tracker import FieldError

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

AnonymousUser.__hacs_base_content_type__ = HACS_CONTENT_TYPE_USER
logger = logging.getLogger("hacs.db.models.base")

"""
Hacs Model short name map:
1. hacs_usm = UserModel (refer to any active user model)
2. hacs_wfl = HacsWorkflowModel
3. hacs_ctr = ContentType Model
4. hacs_grp = HacsGroupModel
5. hacs_rlm = HacsRoleModel
6. hacs_prm = HacsPermissionModel
7. hacs_cnr = HacsContainerModel
"""
#################
# MIXIN CLASSES #
#################


class HacsUserFieldMixin(models.Model):
    """
    """
    roles = models.ManyToManyField(
        'hacs.HacsRoleModel',
        related_name="hacs_rlm_users",
        related_query_name="hacs_rlm_users_set",
        blank=True,
        db_constraint=False
    )
    groups = models.ManyToManyField(
        'hacs.HacsGroupModel',
        related_name="hacs_grp_users",
        related_query_name="hacs_grp_users_set",
        blank=True,
        db_constraint=False
    )

    def has_module_perms(self, app_label):
        """
        :param app_label:
        :return:
        """
        return _user_has_module_perms(self, app_label)

    def has_perm(self, perm, obj=None):
        """
        :param perm:
        :param obj:
        :return:
        """
        return _user_has_perm(self, perm, obj)

    def get_all_permissions(self, obj=None):
        """
        :param obj
        :return:
        """
        return _user_get_all_permissions(self, obj)

    class Meta:
        abstract = True


class HacsBasicFieldMixin(models.Model):
    """
    """
    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, db_index=True)
    name = models.CharField(max_length=127, null=False, blank=True)
    slug = models.SlugField(max_length=127, null=False, blank=True, unique=True, db_index=True)
    created_on = models.DateTimeField(null=False, blank=True, default=timezone.now)
    created_by = ForeignKey(
        settings.AUTH_USER_MODEL,
        db_constraint=False,
        # Prefix hacs
        # um = User Model
        # So pattern prefix_ref:model short name_own class name_actors
        related_name="hacs_usm_{klass}_creators",
        related_query_name="hacs_usm_{klass}_creators_set",
        on_delete=models.DO_NOTHING)
    modified_by = ForeignKey(
        settings.AUTH_USER_MODEL,
        db_constraint=False,
        null=True,
        blank=True,
        related_name="hacs_usm_{klass}_modifiers",
        related_query_name="hacs_usm_{klass}_modifiers_set",
        on_delete=models.DO_NOTHING)
    modified_on = models.DateTimeField(null=True, blank=True)

    def natural_key(self):
        """
        :return:
        """
        return (self.slug, )


class HacsUtilsFieldMixin(models.Model):
    """
    """
    class Meta:
        abstract = True
    # Only list of permissions, by default permission holder has all action permission
    permissions = ManyToManyField(
        'hacs.HacsPermissionModel',
        db_constraint=False,
        related_name="hacs_prm_{klass}_utilities",
        related_query_name="hacs_prm_{klass}_utilities_set"
    )


class HacsSecurityFieldMixin(models.Model):
    """
    """
    class Meta:
        abstract = True
    # Security Guard
    # If workflow is active, then state should have value other than None
    state = models.CharField(max_length=64, null=True, blank=True)
    # Permission should be automatically mapped during state changed!
    # Could achieved by subscribe signals or other way.
    # Although it seems repetitive permission data for each object! but it is required
    # During making maps, should consider parent if allowed
    #
    # Might need clean cache, as well child object cache also
    permissions_actions_map = DictField(null=True, blank=True)
    #
    # Local Roles: {userid: (role1, role2, role3)}
    # user natural key as key and list of role's natural key
    # This attribute is also be tracked!, will be merged with parent local roles if enabled
    # dict update will be happened from top, child will always be win.
    # i.e parent local role: user1: (Manager,) but child has user1: (Editor) so child will be winner
    local_roles = DictField(null=True, blank=True)

    owner = ForeignKey(
        settings.AUTH_USER_MODEL,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        related_name="hacs_usm_{klass}_owners",
        related_query_name="hacs_usm_{klass}_owners_set",
        parent_link=False)

    # If True: this Content object will inherit permission from parent Folder
    # could be come from ContentType object if not manually triggers
    acquire_parent = models.NullBooleanField()


class HacsContentFieldMixin(models.Model):
    """
    """
    class Meta:
        abstract = True
    description = models.TextField(null=True, blank=True)

# Abstract Class
class HacsModelSecurityMixin(models.Model):
    """
    """
    objects = HacsModelManager()
    hacs_base_manager = HacsBaseManager()

    class Meta:
        abstract = True
        default_manager_name = "objects"
        base_manager_name = "hacs_base_manager"

    def delete(self, using=None, keep_parents=False):
        """
        :param using:
        :param keep_parents:
        :return:
        """
        # @TODO: security guard here: action: object.delete
        #
        return super(HacsModelSecurityMixin, self).delete(using, keep_parents)

    def _save_table(self, raw=False, cls=None, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        :param raw:
        :param cls:
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        try:
            _insert = self.hacs_tracker.has_changed('uuid') and\
                      self.hacs_tracker.previous('uuid') is None and\
                      self.uuid is not None
        except FieldError:
                raise
        try:
            if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_STATIC:
                # Simple Static Model Has no state or permissions
                permission_changed = False
            elif self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_UTILS:
                permission_changed = False # self.hacs_tracker.has_changed('permissions')
            elif self.__hacs_base_content_type__ in (HACS_CONTENT_TYPE_CONTAINER, HACS_CONTENT_TYPE_CONTENT):
                if self.hacs_tracker.has_changed('state'):
                    # @TODO: permissions updated here
                    self.update_permissions()
                permission_changed = self.hacs_tracker.has_changed('permissions_actions_map')

                if self.hacs_tracker.has_changed('local_roles') and self.acquire_parent:
                    self.update_local_roles_with_parent()

        except FieldError:
                raise

        ret = super(HacsModelSecurityMixin, self)._save_table(raw, cls, force_insert,force_update, using, update_fields)
        if permission_changed:
            # Send Signal Here
            pass
        return ret

    def update_permissions(self):
        """
        :return:
        """
        # Access HacsContentTypeClass
        content_type_cls = self._meta.base_manager._security_manager().content_type_cls

    def update_local_roles_with_parent(self):
        """
        :param:
        :return:
        """
        if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
            parent_field = 'parent_container_id'
        elif self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTENT:
            parent_field = 'container_id'

        # @TODO: Not sure `GenericForeignKey` immediately available!
        if not getattr(self, parent_field):
            return
        parent = self.container_content_type.get_object_for_this_type(pk=getattr(self, parent_field))
        if parent.local_roles:
            if self.local_roles:
                self.local_roles.update(parent.local_roles)
            else:
                self.local_roles = parent.local_roles





######################
# PUBLIC CLASS       #
######################
class HacsAbstractUser(AbstractBaseUser, HacsUserFieldMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_USER

    class Meta:
        abstract = True


class HacsUtilsModel(HacsModelSecurityMixin, HacsBasicFieldMixin, HacsUtilsFieldMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_UTILS
    hacs_tracker = FieldTracker(fields=('uuid', ))

    class Meta:
        abstract = True
        hacs_default_permissions = ('hacs.ManageUtilsContent', )


class HacsContainerModel(HacsModelSecurityMixin, HacsBasicFieldMixin, HacsContentFieldMixin, HacsSecurityFieldMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_CONTAINER
    hacs_tracker = FieldTracker(fields=('uuid', 'state', 'local_roles', 'permissions_actions_map',))
    # If need other than custom ContentType\s workflow
    workflow = ForeignKey(
        "hacs.HacsWorkflowModel",
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="hacs_wfl_{klass}_containers",
        related_query_name="hacs_wfl_{klass}_containers_set"
    )
    # Container Relation Start
    # See: https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#generic-relations
    container_content_type = ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        validators=[],
        null=True,
        blank=True,
        related_name="hacs_cnr_{klass}_children",
        related_query_name="hacs_cnr_{klass}_children_set"
    )
    # @TODO: on conditional validator should implemented. i.e if `container_content_type` has value,
    # it should not be empty
    parent_container_id = models.PositiveIntegerField(null=True, blank=True)
    parent_container_object = GenericForeignKey('container_content_type', 'parent_container_id', )
    # Container Relation End
    # This field will be effective for state of shared, locked
    recursive = models.NullBooleanField(null=True, blank=True)

    class Meta:
        abstract = True
        hacs_default_permissions = (
            ('object.view', ('hacs.ViewContent',)),
            ('object.create', ('hacs.AddContent',)),
            ('object.edit', ('hacs.ModifyContent',)),
            ('object.delete', ('hacs.DeleteContent',)),
            ('list.traverse', ("hacs.CanTraverseContainer", )),
            ('list.view', ("hacs.CanTraverseContainer", "hacs.CanListObjects", ))
        )

    def update_children_local_roles(self):
        """
        :return:
        """
        # @TODO: this is complicated need to define easy way. could be time consuming task.
        # Have to search all children


class HacsItemModel(HacsModelSecurityMixin, HacsBasicFieldMixin, HacsContentFieldMixin, HacsSecurityFieldMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_CONTENT
    hacs_tracker = FieldTracker(fields=('uuid', 'state', 'local_roles', 'permissions_actions_map',))
    # Container Relation Start
    container_content_type = ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        validators=[],
        null=True,
        blank=True,
        related_name="hacs_cnr_{klass}_items",
        related_query_name="hacs_cnr_{klass}_items_set"
    )
    # @TODO: on conditional validator should implemented. i.e if `container_content_type` has value,
    # it should not be empty
    container_id = models.PositiveIntegerField(null=True, blank=True)
    container_object = GenericForeignKey('container_content_type', 'container_id',)
    # Container Relation End

    class Meta:
        abstract = True
        hacs_default_permissions = (
            ('object.view', ('hacs.ViewContent', )),
            ('object.create', ('hacs.AddContent', )),
            ('object.edit', ('hacs.ModifyContent', )),
            ('object.delete', ('hacs.DeleteContent', )),
        )


class HacsStaticModel(HacsModelSecurityMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_STATIC
    objects = HacsStaticModelManager()
    hacs_tracker = FieldTracker(fields=('uuid',))

    uuid = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, db_index=True)
    name = models.CharField(max_length=127, null=False, blank=False, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    # This field will be defined, if current object is hacs default, that is non removal
    is_system = models.BooleanField(default=False)

    class Meta:
        abstract = True
        default_manager_name = "objects"
        hacs_default_permissions = ('hacs.ManageStaticContent', )

    def natural_key(self):
        """
        :return:
        """
        return (self.name,)
