# -*- coding: utf-8 -*-
# ++ This file `base.py` is generated at 10/24/16 6:16 PM ++
from __future__ import unicode_literals
import uuid
import logging
from django.utils import six
from django.dispatch import receiver
from django.db import models
from django.conf import settings
from django.utils import timezone
from collections import defaultdict
from django.db.models.signals import class_prepared
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import _user_has_module_perms
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey

from hacs.fields import ForeignKey
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_USER
from hacs.globals import HACS_CONTENT_TYPE_UTILS
from hacs.globals import HACS_CONTENT_TYPE_STATIC
from hacs.helpers import get_contenttype_model
from hacs.security.helpers import HACS_OBJECT_EDIT_ACTION
from hacs.security.helpers import HACS_OBJECT_CREATE_ACTION
from hacs.security.helpers import HACS_OBJECT_DELETE_ACTION
from hacs.security.helpers import _user_get_all_permissions
from hacs.fields import JSONField
from .manager import HacsBaseManager, \
    HacsModelManager, \
    HacsStaticModelManager
from .tracker import FieldTracker
from .tracker import FieldError

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


logger = logging.getLogger("hacs.db.models.base")


@receiver(class_prepared)
def apply_default_permissions(sender, **kwargs):
    """
    :param sender:
    :param kwargs:
    :return:
    """
    # We are ignoring non HACS models
    if getattr(sender, '__hacs_base_content_type__', None) is None:
        return

    if sender._meta.abstract:
        return

    try:
        logging.debug("User defined permissions %s found! \n Respect it! no overwrite." % sender._meta.hacs_default_permissions)
    except AttributeError:
        if sender.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTENT:
            sender._meta.hacs_default_permissions = (
                ('object.view', ('hacs.ViewContent', )),
                ('object.create', ('hacs.AddContent',)),
                ('object.edit', ('hacs.ModifyContent', )),
                ('object.delete', ('hacs.DeleteContent', )),
            )
        elif sender.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
            sender._meta.hacs_default_permissions = (
                ('object.view', ('hacs.ViewContent',)),
                ('object.create', ('hacs.AddContent',)),
                ('object.edit', ('hacs.ModifyContent',)),
                ('object.delete', ('hacs.DeleteContent',)),
                ('list.traverse', ("hacs.CanTraverseContainer", )),
                ('list.view', ("hacs.CanTraverseContainer", "hacs.CanListObjects", ))
            )
        elif sender.__hacs_base_content_type__ == HACS_CONTENT_TYPE_UTILS:
            sender._meta.hacs_default_permissions = ('hacs.ManageUtilsContent', )

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
    permissions = JSONField(null=True, blank=True, validators=[])


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
    permissions_actions_map = JSONField(null=True, blank=True)
    #
    # Local Roles: {userid: (role1, role2, role3)}
    # user natural key as key and list of role's natural key
    # This attribute is also be tracked!, will be merged with parent local roles if enabled
    # dict update will be happened from top, child will always be win.
    # i.e parent local role: user1: (Manager,) but child has user1: (Editor) so child will be winner
    local_roles = JSONField(null=True, blank=True)

    owner = ForeignKey(
        settings.AUTH_USER_MODEL,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        related_name="hacs_usm_{klass}_owners",
        related_query_name="hacs_usm_{klass}_owners_set",
        parent_link=False)
    acquired_owners = JSONField(null=True, blank=True,)
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
        security_manager = self._meta.default_manager._security_manager()
        security_manager.check_obj_permission(self, action=HACS_OBJECT_DELETE_ACTION)
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
                if self.permissions is None and _insert:
                    self.update_permissions()

                permission_changed = self.hacs_tracker.has_changed('permissions')

            elif self.__hacs_base_content_type__ in (HACS_CONTENT_TYPE_CONTAINER, HACS_CONTENT_TYPE_CONTENT):

                hacs_ct = get_contenttype_model().objects.get_for_model(self._meta.model)
                if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
                    parent_container = getattr(self, 'parent_container_object')
                elif self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTENT:
                    parent_container = getattr(self, 'container_object')

                if self.hacs_tracker.has_changed('acquire_parent') and not _insert:
                    # Only Applicable on Update
                    self.apply_aquire_parent_changed()

                _workflow = None
                if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
                    # Try From Container Default
                    _workflow = self.workflow

                if _workflow is None:
                    # Try From content type
                    _workflow = hacs_ct.workflow

                if _workflow is None and self.acquire_parent and parent_container is not None:
                    # We respect parent settings (allow acquiring)

                    if parent_container.recursive:
                        _workflow = parent_container.workflow

                if _insert and _workflow is not None and self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
                    # Set workflow
                    self.workflow = _workflow

                if _insert and self.state is None:
                    if _workflow:
                        self.state = _workflow.default_state

                if self.hacs_tracker.has_changed('state') or\
                    (_insert and self.permissions_actions_map is None and _workflow is None):
                    # @TODO: permissions updated here
                    self.update_permissions(_workflow, hacs_ct)

                permission_changed = self.hacs_tracker.has_changed('permissions_actions_map')

                if (self.hacs_tracker.has_changed('local_roles') or _insert) and self.acquire_parent:
                    self.update_local_roles_with_parent()

                if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
                    if self.hacs_tracker.has_changed('recursive') and not _insert:
                        self.apply_recursive_changed()
                # For Insert Action, Parent owners will be acquired
                if _insert and parent_container:
                    self.update_acquired_owners(parent_container)
                # Auto assign ownership while  inserting
                if _insert and self.owner is None:
                    self.owner = self.created_by

        except FieldError:
                raise
        # Security Check Here!
        security_manager = self._meta.default_manager._security_manager()
        security_manager.check_obj_permission(self,
                                              action=_insert and HACS_OBJECT_CREATE_ACTION or HACS_OBJECT_EDIT_ACTION)

        result = super(HacsModelSecurityMixin, self)._save_table(raw, cls, force_insert,force_update, using,
                                                                 update_fields)
        if permission_changed:
            # Send Signal Here
            pass
        return result

    def update_permissions(self, workflow=None, hacs_contenttype=None):
        """
        :param workflow
        :param hacs_contenttype
        :return:
        """
        if hacs_contenttype is None:
            # yep! utils model
            permissions = set()
            for permission in tuple(self._meta.hacs_default_permissions) + tuple(self._meta.permissions or []):
                if isinstance(permission, six.string_types):
                    permissions.add(permission)

                elif isinstance(permission, (tuple, list)):
                    # we will catch action
                    if isinstance(permission[1], six.string_types):
                        permissions.add(permission[1])
                    elif isinstance(permission[1], (list, tuple)):
                        permissions = permissions.union(permission[1])

            self.permissions = tuple(permissions)
            return

        if workflow:
            try:
                self.permissions_actions_map = workflow.states_permissions_map[self.state]
            except KeyError:
                # @TODO: need to meaningful error
                raise
        else:
            # No workflow! we are going to search from contenttype
            permissions = hacs_contenttype.permissions_actions_map.copy() or defaultdict()
            permissions.pop('object.create', None)

            if not permissions:

                for permission in self._meta.hacs_default_permissions:

                    if isinstance(permission, six.string_types) or (isinstance(permission, (tuple, list)) and
                                                                            2 != len(permission)):
                        # We don't accept invalid permission format for this contenttype
                        continue

                    permissions[permission[0]] = permission[1]

                for permission in self._meta.permissions or []:

                    if isinstance(permission, six.string_types) or (isinstance(permission, (tuple, list)) and
                                                                            2 != len(permission)):
                        # We don't accept invalid permission format for this contenttype
                        continue
                    try:
                        # Trying to combine with default
                        temp = set(permissions[permission[0]])
                        permissions[permission[0]] = temp.union(permission[1])
                    except KeyError:
                        permissions[permission[0]] = permission[1]

            self.permissions_actions_map = permissions

    def update_local_roles_with_parent(self):
        """
        :param:
        :return:
        """
        if self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTAINER:
            parent = getattr(self, 'parent_container_object')
        elif self.__hacs_base_content_type__ == HACS_CONTENT_TYPE_CONTENT:
            parent = getattr(self, 'container_object')

        # @TODO: Not sure `GenericForeignKey` immediately available!
        if parent is None:
            return

        if parent.local_roles:
            if self.local_roles:
                self.local_roles.update(parent.local_roles)
            else:
                self.local_roles = parent.local_roles

    def update_acquired_owners(self, parent):
        """
        :param parent:
        :return:
        """
        owners = set()
        if parent.acquired_owners:
            owners = owners.union(parent.acquired_owners)
        owners.add(getattr(parent.owner, parent.owner.USERNAME_FIELD))

        self.acquired_owners = list(owners)

    def apply_aquire_parent_changed(self):
        """
        :return:
        """

    def apply_recursive_changed(self):
        """
        :return:
        """

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
    hacs_tracker = FieldTracker(fields=('uuid', 'permissions', ))

    class Meta:
        abstract = True


class HacsContainerModel(HacsModelSecurityMixin, HacsBasicFieldMixin, HacsContentFieldMixin, HacsSecurityFieldMixin):
    """
    """
    __hacs_base_content_type__ = HACS_CONTENT_TYPE_CONTAINER
    hacs_tracker = FieldTracker(fields=('uuid', 'state', 'owner','local_roles', 'permissions_actions_map', 'workflow',
                                        'acquire_parent', 'recursive'))
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
    hacs_tracker = FieldTracker(fields=('uuid', 'state', 'owner', 'local_roles', 'permissions_actions_map', 'acquire_parent', ))
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
