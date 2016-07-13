from __future__ import unicode_literals

from django.db import models
from django.apps import apps
from django.utils import six
from django.utils import timezone
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import DictField
from .fields import SequenceField
from .validators import UrlModulesValidator
from .validators import HttpHandlerValidator
from .validators import ContentTypeValidator


if not apps.is_installed('django.contrib.admin'):
    # Fallback LogEntry Model, if admin app not installed
    from django.contrib.admin.models import LogEntry as django_LogEntry

    class LogEntry(django_LogEntry):
        pass

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class RoutingTableManager(models.Manager):
    """"""
    use_in_migrations = True

    def get_by_natural_key(self, route_name):
        """
        :param route_name:
        :return:
        """
        return self.get(route_name=route_name)


@python_2_unicode_compatible
class RoutingTable(models.Model):
    """
    JSON Field Permitted Format/Python Data pattern
    -----------------------------------------------
    urls: [{'prefix': None, 'url_module': None, namespace=None, app_name: None}]
    OR [{'prefix': None, 'url_module': (module, app_name), namespace=None}]

    handlers: {'handler400': None, 'handler403': None, 'handler404': None, 'handler500': None}
    """
    route_name = models.SlugField(_('route name'),  null=False, blank=False, unique=True, db_index=True, max_length=127)
    description = models.TextField(_('description'), null=True, blank=True)
    urls = SequenceField(_('URLs'), null=False, blank=False, validators=[UrlModulesValidator()])
    handlers = DictField(_('Handlers'), null=True, blank=True, default='', validators=[HttpHandlerValidator()])
    generated_module = models.CharField(_('Generated Module'), null=True, blank=True, default=None, max_length=255)
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    is_deleted = models.BooleanField(_('Soft Delete'), null=False, blank=True, default=False)
    created_on = models.DateTimeField(_('Created On'), blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

    objects = RoutingTableManager()

    class Meta:
        db_table = 'hacs_routing_table'
        verbose_name = _('routing table')
        verbose_name_plural = _('routes table')

    def natural_key(self):
        """
        :return:
        """
        return (self.route_name, )

    def __str__(self):
        """
        """
        return self.route_name


class SiteRoutingRulesManager(models.Manager):
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
class SiteRoutingRules(models.Model):

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
    created_on = models.DateTimeField(_('Created On'), blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

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


class ContentTypeRoutingRulesManager(models.Manager):
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
class ContentTypeRoutingRules(models.Model):

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
    created_on = models.DateTimeField(_('Created On'),  blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

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
            # Right now `natural_key` is not implemented by django, but would be good if they do
            site_natural_key = self.site.pk

        return (site_natural_key, self.content_type.natural_key(), self.object_id, )

    natural_key.dependencies = ["hacs.RoutingTable", "sites.Site", "contenttypes.ContentType"]

    def __str__(self):
        """"""
        return "%s:%s:%s's routing rules" % (self.site.domain, self.content_type.app_label + "." +
                                             self.content_type.model, self.object_id)
