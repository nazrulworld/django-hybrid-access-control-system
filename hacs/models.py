#  -*- coding: utf-8 -*-
from django.db import models
from django.apps import apps
from django.utils import six
from django.conf import settings
from collections import defaultdict
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import JSONField

from .fields import DictField
from .fields import SequenceField
from .validators import UrlModulesValidator
from .validators import HttpHandlerValidator
from .validators import ContentTypeValidator

from hacs.db.models import HacsModelManager
from hacs.db.models import HacsUtilsModel
from hacs.db.models import BaseUserManager
from hacs.db.models.base import HacsAbstractUser
from hacs.db.models import HacsStaticModel
from hacs.defaults import HACS_DEFAULT_STATE
from hacs.security.helpers import HACS_CONTENT_ADD_PERMISSION
from hacs.security.helpers import HACS_OBJECT_CREATE_ACTION

if not apps.is_installed('django.contrib.admin'):
    # Fallback LogEntry Model, if admin app not installed
    from django.contrib.admin.models import LogEntry as django_LogEntry

    class LogEntry(django_LogEntry):
         pass

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [
    str(x) for x in (
        "HacsRoleModel",
        "HacsGroupModel",
        "HacsPermissionModel",
        "HacsContentType",
        "HacsWorkflowModel",
        "HacsUserModel",
        "RoutingTable",
        "SiteRoutingRules",
        "ContentTypeRoutingRules",
    )
]
# Hacs Component Model


@python_2_unicode_compatible
class HacsRoleModel(HacsStaticModel):
    """
    """
    parent = models.ForeignKey(
        'hacs.HacsRoleModel',
        db_constraint=False,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="hacs_rlm_children",
        related_query_name="hacs_rlm_children_set"
    )

    class Meta:
        app_label = "hacs"
        db_table = "hacs_roles"
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        """"""
        return self.name


@python_2_unicode_compatible
class HacsGroupModel(HacsStaticModel):

    roles = models.ManyToManyField(
        "hacs.HacsRoleModel",
        db_constraint=False,
        related_name="hacs_rlm_groups",
        related_query_name="hacs_rlm_groups_set"
    )

    class Meta:
        app_label = "hacs"
        db_table = "hacs_groups"
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        """"""
        return self.name


@python_2_unicode_compatible
class HacsPermissionModel(HacsStaticModel):

    roles = models.ManyToManyField(
        "hacs.HacsRoleModel",
        db_constraint=False,
        related_name="hacs_rlm_permissions",
        related_query_name="hacs_rlm_permissions_set"
    )
    parent = models.ForeignKey(
        'self',
        db_constraint=False,
        null=True,
        blank=True,
        related_name="hacs_prm_children",
        related_query_name="hacs_prm_children_set"
    )

    class Meta:
        app_label = "hacs"
        db_table = "hacs_permissions"
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")

    def __str__(self):
        """"""
        return self.name


class HacsContentTypeManager(HacsModelManager):
    """
    """
    use_in_migrations = True

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        super(HacsContentTypeManager, self).__init__(*args, **kwargs)
        # django.contenttype style!
        self._cache = defaultdict()

    def get_by_natural_key(self, app_label, model):
        """
        :param app_label:
        :param model:
        :return:
        """
        try:
            hacs_ct = self._cache[self.db][(app_label, model)]
        except KeyError:
            ct = ContentType.objects.get_by_natural_key(app_label, model)
            hacs_ct = self.select_related('content_type', 'workflow').\
                prefetch_related('allowed_content_types').get(content_type=ct)
            # now are caching
            self._add_to_cache(self.db, hacs_ct)

        return hacs_ct

    def get_for_model(self, model, for_concrete_model=True):
        """
        :param model:
        :param for_concrete_model:
        :return:
        """
        ct = ContentType.objects.get_for_model(model, for_concrete_model)

        try:
            hacs_ct = self._cache[self.db][(ct.app_label, ct.model)]
        except KeyError:
            hacs_ct = self.select_related('content_type', 'workflow').\
                prefetch_related('allowed_content_types').get(content_type=ct)
            self._add_to_cache(self.db, hacs_ct)

        return hacs_ct

    def get_for_id(self, id):
        """
        :param id:
        :return:
        """
        try:
            hacs_ct = self._cache[self.db][id]
        except KeyError:
            ct = ContentType.objects.get_for_id(id)
            hacs_ct = self.select_related('content_type', 'workflow').\
                prefetch_related('allowed_content_types').get(content_type=ct)
            self._add_to_cache(self.db, hacs_ct)

        return hacs_ct

    def clear_cache(self):
        """
        :return:
        """
        self._cache.clear()

    def _add_to_cache(self, using, hacs_ct):
        """
        :param using:
        :param hacs_ct:
        :return:
        """
        key = (hacs_ct.content_type.app_label, hacs_ct.content_type.model)
        self._cache.setdefault(using, {})[key] = hacs_ct
        self._cache.setdefault(using, {})[hacs_ct.content_type.id] = hacs_ct


@python_2_unicode_compatible
class HacsContentType(HacsUtilsModel):
    """
    """
    objects = HacsContentTypeManager()

    # Validators: only HacsContainer & HacsContent type are allowed
    content_type = models.OneToOneField(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        unique=True,
        validators=[]
    )
    # This could be applicable for Container or Item
    globally_allowed = models.BooleanField(blank=True, null=False)

    # Only applicable for Container Type Model
    allowed_content_types = models.ManyToManyField(
        'contenttypes.ContentType',
        blank=True,
        db_constraint=False,
        related_name="hacs_ctr_hctype_ctypes",
        related_query_name="hacs_ctr_hctype_ctypes_set"
    )
    # @TODO: need to decide workflow could be acquired. I think should not but respect parent permission (at least view)
    workflow = models.ForeignKey(
        "hacs.HacsWorkflowModel",
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="hacs_wfl_HacsContentType_ctypes",
        related_query_name="hacs_wfl_HacsContentType_ctypes_set"
    )
    # A dictionary map for content type permission
    # Data Format: {'action': (permission1. permission2)}
    # Usually should contain one permission 'object.create' map, when workflow is active
    # because other permissions will be ignored if workflow is available
    permissions_actions_map = DictField(null=True, default={HACS_OBJECT_CREATE_ACTION: [HACS_CONTENT_ADD_PERMISSION, ]})

    class Meta:
        app_label = "hacs"
        db_table = "hacs_contenttypes"

    def natural_key(self):
        """"
         :return:
        """
        return self.content_type.natural_key()

    def __str__(self):
        """"""
        return self.content_type.__str__()
# END


# Special Class
@python_2_unicode_compatible
class HacsWorkflowModel(HacsUtilsModel):
    """
    """

    # If you want to use custom role map for each permission. Other by default global map will be respected.
    # Data Format: {'permission name': ('role1', 'role2')}
    permissions_map = DictField(null=True, blank=True)

    # Which object states will be handled by this workflow. Also will be used as validator while applied this workflow
    # on specified content type.
    states = SequenceField(null=True, blank=True)

    # Targeted state after object is created
    default_state = models.CharField(
        max_length=64,
        null=False,
        blank=True,
        default=getattr(settings, 'HACS_DEFAULT_STATE', HACS_DEFAULT_STATE))

    # This the important for object guard. Security Manger actually lookup with this.
    # Validation Rule: if one state has no requested action by default will be rejected even if Manager User.
    # Data Format: {
    #   'state': {'action1': ('permission1', 'permission2'), 'action2': ('permission1', 'permission2')}
    # }
    states_permissions_map = JSONField(null=True, blank=True)

    # These are view/actions name that will change the state of an object. User should use this action instead of
    # direct change the state of object.
    # Transitions description could be another place, here only key is used.
    # Data Format: {'transition': {'target state': '', 'required permissions': () }}
    transitions = DictField(null=True, blank=True)

    class Meta:
        app_label = "hacs"
        db_table = "hacs_workflows"
        verbose_name = _("workflow")
        verbose_name_plural = _("workflows")

    def __str__(self):
        """
        :return:
        """
        return "<%s: %s>" % (self.__class__.__name__, self.name)


@python_2_unicode_compatible
class RoutingTable(HacsUtilsModel):
    """
    JSON Field Permitted Format/Python Data pattern
    -----------------------------------------------
    urls: [{'prefix': None, 'url_module': None, namespace=None, app_name: None}]
    OR [{'prefix': None, 'url_module': (module, app_name), namespace=None}]

    handlers: {'handler400': None, 'handler403': None, 'handler404': None, 'handler500': None}
    """
    description = models.TextField(_('description'), null=True, blank=True)
    urls = SequenceField(_('URLs'), null=False, blank=False, validators=[UrlModulesValidator()])
    handlers = DictField(_('Handlers'), null=True, blank=True, default='', validators=[HttpHandlerValidator()])
    generated_module = models.CharField(_('Generated Module'), null=True, blank=True, default=None, max_length=255)
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    is_deleted = models.BooleanField(_('Soft Delete'), null=False, blank=True, default=False)

    class Meta:
        db_table = 'hacs_routing_table'
        verbose_name = _('routing table')
        verbose_name_plural = _('routes table')

    def __str__(self):
        """
        """
        return self.name


class SiteRoutingRulesManager(HacsModelManager):
    """ """
    use_in_migrations = True

    def get_by_natural_key(self, site_natural_key):
        """
        :param site_natural_key:
        :return:
        """
        if isinstance(site_natural_key, six.string_types):
            site_natural_key = (site_natural_key,)

        try:
            if not isinstance(site_natural_key, (list, tuple,)):
                snk = (site_natural_key, )
            else:
                snk = site_natural_key
            site = Site.objects.db_manager(self.db).get_by_natural_key(*snk)
        except AttributeError:
            if isinstance(site_natural_key, six.integer_types):
                site = Site.objects.db_manager(self.db).get(pk=site_natural_key)
            else:
                raise

        return self.get(site=site)


@python_2_unicode_compatible
class SiteRoutingRules(HacsUtilsModel):

    """
    """
    route = models.ForeignKey(RoutingTable,
                              on_delete=models.CASCADE,
                              db_column='route_id',
                              db_constraint=False,
                              related_name='hacs_route_sites')
    site = models.OneToOneField(Site,
                             on_delete=models.CASCADE,
                             unique=True,
                             null=False,
                             blank=False,
                             related_name='hacs_site_routes')

    allowed_method = SequenceField(_('Allowed Method'), null=True, blank=True)
    blacklisted_uri = models.CharField(
        _('blacklisted uri'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('regex formatted uri those will be treated as blacklisted and request will be discarded by firewall'))

    whitelisted_uri = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('regex formatted uri those will be treated as whitelisted and request will '
                   'be discarded by firewall if uri not match'))

    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    maintenance_mode = models.BooleanField(
        _('Maintenance Mode'),
        null=False,
        blank=True,
        default=False,
        help_text=_('Firewall will only response maintenance view and prevent any further execution '
                    'for all request if it is on'))

    objects = SiteRoutingRulesManager()

    class Meta:
        db_table = 'hacs_sites_routing_rules'
        verbose_name = _('site routing rules')
        verbose_name_plural = _('sites routing rules')

    def natural_key(self):
        """
        :return:
        """
        try:
            site_natural_key = self.site.natural_key()
        except AttributeError:
            # Right now `natural_key` is not implemented by django, but would be good if they do
            site_natural_key = self.site.pk
        return (site_natural_key, )

    natural_key.dependencies = ["hacs.RoutingTable", "sites.Site"]

    def __str__(self):
        """"""
        return "%s's routing rules" % self.site.domain


class ContentTypeRoutingRulesManager(HacsModelManager):
    """ """
    use_in_migrations = True

    def get_by_natural_key(self, site_nk, content_type_nk, object_id):
        """
        :param site_nk:
        :param content_type_nk
        :param object_id
        :return:
        """
        if isinstance(site_nk, six.string_types):
            site_nk = (site_nk,)

        if isinstance(content_type_nk, six.string_types):
            content_type_nk = (content_type_nk,)

        try:
            if not isinstance(site_nk, (list, tuple)):
                snk = (site_nk, )
            else:
                snk = site_nk
            site = Site.objects.db_manager(self.db).get_by_natural_key(*snk)
        except AttributeError:
            if isinstance(site_nk, six.integer_types):
                site = Site.objects.db_manager(self.db).get(pk=site_nk)
            else:
                raise

        return self.get(
            site=site,
            content_type=ContentType.objects.db_manager(self.db).get_by_natural_key(*content_type_nk),
            object_id=object_id
        )


@python_2_unicode_compatible
class ContentTypeRoutingRules(HacsUtilsModel):

    """
    """
    route = models.ForeignKey(RoutingTable,
                              on_delete=models.CASCADE,
                              db_column='route_id',
                              db_constraint=False,
                              related_name='hacs_route_contenttypes',
                              validators=[],
                              )
    site = models.ForeignKey(Site,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='hacs_site_contenttypes_at_routing_rules'
                            )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, validators=[ContentTypeValidator()])
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    allowed_method = SequenceField(_('Allowed Method'), null=True, blank=True)
    blacklisted_uri = models.CharField(
        _('blacklisted uri'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_('regex formatted uri those will be treated as blacklisted and request will be '
                    'discarded by firewall'))
    whitelisted_uri = models.CharField(
        _('whitelisted uri'),
        max_length=255,
        null=True,
         blank=True,
         help_text='regex formatted uri those will be treated as whitelisted and request will '
                   'be discarded by firewall if uri not match')
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    objects = ContentTypeRoutingRulesManager()

    class Meta:
        db_table = 'hacs_ct_routing_rules'
        verbose_name = _('content type routing rules')
        verbose_name_plural = _('content types routing rules')
        unique_together = (("site", "content_type", "object_id"),)

    def natural_key(self):
        """
        :return:
        """
        try:
            site_natural_key = self.site.natural_key()
        except AttributeError:
            #  Bellow Django 1.10 `natural_key` is not implemented by django, but would be good if they do
            site_natural_key = self.site.pk
        return (site_natural_key, self.content_type.natural_key(), self.object_id, )

    natural_key.dependencies = ["hacs.RoutingTable", "sites.Site", "contenttypes.ContentType"]

    def __str__(self):
        """
        :return:
        """
        return "%s:%s:%s's routing rules" % (self.site.domain, self.content_type.app_label + "." +
                                              self.content_type.model, self.object_id)


class HacsUserManger(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email as username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


@python_2_unicode_compatible
class HacsUserModel(HacsAbstractUser):
    """"""

    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=127, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=False, null=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = HacsUserManger()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        app_label = "hacs"
        db_table = "hacs_users"
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        :return:
        """
        return "%s %s" % (self.first_name, self.last_name or "")

    def get_short_name(self):
        """
        :return:
        """
        return self.first_name

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    def __str__(self):
        """
        :return:
        """
        return "<%s : %s %s>" % (getattr(self, self.USERNAME_FIELD), self.first_name, self.last_name or "")
