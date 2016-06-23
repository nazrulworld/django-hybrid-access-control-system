# -*- coding: utf-8 -*-
# ++ This file `middleware.py` is generated at 3/3/16 6:05 AM ++
from __future__ import unicode_literals
import re
import logging
import warnings
from collections import defaultdict
from django.apps import apps
from django.utils import six
from django.conf import settings
from django.utils.encoding import smart_bytes
from django.core.cache import caches
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
try:
    # expect django version 1.10.x or higher
    from django.urls import get_resolver, Resolver404
except ImportError:
    from django.core.urlresolvers import get_resolver, Resolver404
from django.utils.functional import cached_property
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from .globals import HACS_APP_NAME
from .models import ContentTypeRoutingRules
from .defaults import HACS_FALLBACK_URLCONF
from .defaults import HACS_CACHE_SETTING_NAME
from .lru_wrapped import get_user_key
from .lru_wrapped import get_group_key
from .lru_wrapped import site_in_maintenance_mode
from .utils import generate_urlconf_file_on_demand
from .lru_wrapped import get_generated_urlconf_file
from .lru_wrapped import get_generated_urlconf_module
from .lru_wrapped import get_site_urlconf
from .lru_wrapped import get_site_blacklisted_uri
from .lru_wrapped import get_site_whitelisted_uri
from .lru_wrapped import get_site_http_methods
from .views.errors import maintenance_mode
from .views.errors import service_unavailable
from .views.errors import http_method_not_permitted

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger('hacs.middleware')
UserModel = get_user_model()


class DynamicRouteMiddleware(object):
    """ """
    name = 'hacs.middleware.DynamicRouteMiddleware'

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        if self._validate:
            pass

        urlconf = get_site_urlconf(getattr(request, 'site', get_current_site(request)))

        request.urlconf = urlconf

    @cached_property
    def _validate(self):
        """
        :return:
        """
        errors = []
        if not apps.is_installed(HACS_APP_NAME):
            errors.append(_("%s need to be added into settings.INSTALLED_APPS" % HACS_APP_NAME))

        if not apps.is_installed('django.contrib.contenttypes'):
            errors.append(_("django.contrib.contenttypes need to be added into settings.INSTALLED_APPS"))

        if not apps.is_installed('django.contrib.sites'):
            errors.append(_("django.contrib.sites need to be added into settings.INSTALLED_APPS"))

        try:
            site_middleware_position = \
                settings.MIDDLEWARE_CLASSES.index('django.contrib.sites.middleware.CurrentSiteMiddleware')
        except ValueError:
            errors.append(_("django.contrib.sites.middleware.CurrentSiteMiddleware need to be "
                            "added into settings.MIDDLEWARE_CLASSES"))
        else:
            if site_middleware_position > settings.MIDDLEWARE_CLASSES.index(self.name):
                errors.append(_('django.contrib.sites.middleware.CurrentSiteMiddleware\'s position should be before ' +
                                self.name))
        if errors:
            raise ImproperlyConfigured(_("Please fix: %s" % ' | '.join(errors)))

        return True


class FirewallMiddleware(object):
    """     """
    name = 'hacs.middleware.FirewallMiddleware'
    cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        if self._validate:
            pass
        # #################################
        # Maintenance Mode Checking Start #
        # #################################
        if site_in_maintenance_mode(get_current_site(request)):
            # we directly response (view)
            return maintenance_mode(request)

        # Let's check for any black/white listed uri
        request_path = request.path_info
        if get_site_blacklisted_uri(get_current_site(request)):
            match = re.compile(smart_bytes(get_site_blacklisted_uri(get_current_site(request))))
            if match.match(request_path):
                return service_unavailable(request)

        if get_site_whitelisted_uri(get_current_site(request)):
            match = re.compile(smart_bytes(get_site_whitelisted_uri(get_current_site(request))))
            if not match.match(request_path):
                return service_unavailable(request)

        # Let's check if HTTP Methods constraint is applicable
        if get_site_http_methods(get_current_site(request)):
            if request.method not in get_site_http_methods():
                return http_method_not_permitted(request)

        if request.user.is_authenticated():
            try:
                user_settings_session = request.session['settings']
            except KeyError:
                request.session['settings'] = dict()
                user_settings_session = request.session['settings']
            try:
                user_settings_session['urlconf']
            except KeyError:
                # There is no urlconf set yet! now assigning
                self.set_auth_user_settings(request)

            user_urlconf = self._calculate_user_urlconf(request_path, user_settings_session)
            if user_urlconf:
                # Now we are ready to check list
                if user_settings_session['blacklisted_uri']:
                    match = re.compile(smart_bytes(user_settings_session['blacklisted_uri']))
                    if match.match(request_path):
                        return service_unavailable(request)

                if user_settings_session['whitelisted_url']:
                    match = re.compile(smart_bytes(user_settings_session['whitelisted_url']))
                    if not match.match(request_path):
                        return service_unavailable(request)

                # Let's check if HTTP Methods constraint is applicable
                if user_settings_session['allowed_http_methods']:
                    if request.method not in user_settings_session['allowed_http_methods']:
                        return http_method_not_permitted(request)

            # lastly we are updating session
            request.session['settings'].update(user_settings_session)
        else:
            # Anonymous User
            user_urlconf = self._calculate_anonymous_urlconf(request)

        if user_urlconf:
            request.urlconf = user_urlconf
        else:
            # Let's check already set by DynamicRouteMiddleware
            if not getattr(request, 'urlconf', None):
                warnings.warn("urlconf is neither set by DynamicRoutingMiddleware nor from django settings.")
                request.urlconf = getattr(settings, 'HACS_FALLBACK_URLCONF', HACS_FALLBACK_URLCONF)

    def set_auth_user_settings(self, request):
        """
        :param request:
        :return:
        """
        # Try from cache
        user_settings_cache = self.cache.get(get_user_key(request))
        if user_settings_cache and user_settings_cache.get('urlconf', None):
            request.session['settings'].update({
                'urlconf': user_settings_cache.get('urlconf'),
                'allowed_http_methods': user_settings_cache.get('allowed_http_methods'),
                'blacklisted_uri': user_settings_cache.get('blacklisted_uri'),
                'whitelisted_uri': user_settings_cache.get('blacklisted_uri'),
                'groups': user_settings_cache.get('groups')
            })
            return None

        # No cache
        initial_data = {
            'urlconf': None,
            'allowed_http_methods': None,
            'blacklisted_uri': None,
            'whitelisted_uri': None,
            'groups': []
        }
        for group in request.user.groups.all():
            initial_data['groups'].append((get_group_key(request, group), group.natural_key()))
            # We will trigger auth group settings from here
            self.set_auth_group_settings(request, group, False)

        if not user_settings_cache:
            user_settings_cache = defaultdict()
        try:
            user_route_rules = ContentTypeRoutingRules.objects.get(
                site=request.site,
                content_type=ContentType.objects.get_for_model(UserModel),
                object_id=request.user.is_authenticated() and request.user.pk or 0)

        except ContentTypeRoutingRules.DoesNotExist:
            # User Has No Route Will use group's route rules if exist
            pass
        else:
            # Check if urlconf file need to be created
            generate_urlconf_file_on_demand(user_route_rules.route)

            initial_data.update({
                'urlconf': get_generated_urlconf_module(get_generated_urlconf_file(user_route_rules.route.route_name)),
                'allowed_http_methods': user_route_rules.allowed_method,
                'blacklisted_uri': user_route_rules.blacklisted_uri,
                'whitelisted_uri': user_route_rules.whitelisted_uri,
                'is_active': user_route_rules.is_active
            })

        # Update Session
        request.session['settings'].update(initial_data)
        # Set Cache
        self.cache.set(get_user_key(request), user_settings_cache.update(initial_data))

    def set_auth_group_settings(self, request, group, force_update=True):
        """
        :param request:
        :param group:
        :param force_update:
        :return:
        """
        # Try from cache
        cache_key = get_group_key(request, group)
        group_settings_cache = self.cache.get(cache_key)

        # No cache
        if not group_settings_cache:
            group_settings_cache = defaultdict()

        if group_settings_cache.get('urlconf', None) and not force_update:
            return

        try:
            group_route_rules = ContentTypeRoutingRules.objects.get(
                content_type=ContentType.objects.get_for_model(Group), object_id=group.id, site=request.site)
        except ContentTypeRoutingRules.DoesNotExist:
            # We do nothing
            pass
        else:
            # we are checking if file need to be created
            generate_urlconf_file_on_demand(group_route_rules.route)
            group_settings_cache.update({
                'urlconf': get_generated_urlconf_module(get_generated_urlconf_file(group_route_rules.route.route_name)),
                'route_id': group_route_rules.route.pk,
                'allowed_http_methods': group_route_rules.allowed_method,
                'blacklisted_uri': group_route_rules.blacklisted_uri,
                'whitelisted_uri': group_route_rules.whitelisted_uri,
                'is_active': group_route_rules.is_active
            })

        # Set Cache
        self.cache.set(cache_key, group_settings_cache)

    @cached_property
    def _validate(self):
        """
        :return:
        """
        errors = []

        try:
            dynamic_route_middleware_position = \
                settings.MIDDLEWARE_CLASSES.index(DynamicRouteMiddleware.name)
        except ValueError:
            errors.append(_("%s need to be "
                            "added into settings.MIDDLEWARE_CLASSES" % DynamicRouteMiddleware.name))
        else:
            if dynamic_route_middleware_position > settings.MIDDLEWARE_CLASSES.index(self.name):
                errors.append(_(DynamicRouteMiddleware.name + '\'s position should be before ' +
                                self.name))
        return True

    def _calculate_user_urlconf(self, request_path, user_settings_session):
        """
        :param request_path:
        :param user_settings_session:
        :return:
        """
        if user_settings_session['urlconf'] and isinstance(user_settings_session['urlconf'], six.string_types):
            return user_settings_session['urlconf']

        elif user_settings_session['groups']:
            _temp = None
            for group_cache_key, group_natural_key in user_settings_session['groups']:
                if not self.cache.get(group_cache_key, {}).get('urlconf', None):
                    continue
                try:
                    resolver = get_resolver(self.cache.get(group_cache_key).get('urlconf'))
                    resolver.resolve(request_path)
                    user_settings_session.update({
                        'allowed_http_methods': self.cache.get(group_cache_key).get('allowed_http_methods'),
                        'blacklisted_uri': self.cache.get(group_cache_key).get('blacklisted_uri'),
                        'whitelisted_uri': self.cache.get(group_cache_key).get('whitelisted_uri'),
                    })
                    _temp = self.cache.get(group_cache_key).get('urlconf')
                    break
                except Resolver404:
                    continue
            # @TODO: need some decision what should do if result is None
            return _temp
        else:
            return None

    def _calculate_anonymous_urlconf(self, request):
        """
        """
        cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        cache_key = get_user_key(request)
        user_settings = cache.get(cache_key) or dict()
        try:
            return user_settings['settings']['urlconf']
        except KeyError:
            try:
                # The hacs convention anonymous user pk is 0
                user_route = ContentTypeRoutingRules.objects.get(
                    site=request.site,
                    content_type=ContentType.objects.get_for_model(UserModel),
                    object_id=0)
                generate_urlconf_file_on_demand(user_route.route)
                urlconf = get_generated_urlconf_module(get_generated_urlconf_file(user_route.route.route_name))
            except ContentTypeRoutingRules.DoesNotExist:
                urlconf = None

            if 'settings' not in user_settings.keys():
                user_settings['settings'] = dict()
            user_settings['settings']['urlconf'] = urlconf
            # Update Cache
            cache.set(cache_key, user_settings, 3600 * 24)

            return urlconf


__all__ = ("DynamicRouteMiddleware", "FirewallMiddleware", )
