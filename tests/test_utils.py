# -*- coding: utf-8 -*-
# ++ This file `test_utils.py` is generated at 3/7/16 6:12 PM ++
from __future__ import unicode_literals
import os
import sys
import pytest
import tempfile
from django.utils import six
from hacs.models import SiteRoutingRules
from django.test import TransactionTestCase
from importlib import import_module
from django.test import RequestFactory
from django.test import override_settings
from django.contrib.sites.shortcuts import get_current_site
from hacs.utils import *
from hacs.helpers import get_user_model
from hacs.security.helpers import get_cache_key

from .path import FIXTURE_PATH

TEST_USER_NAME = 'superuser@test.com'
TEST_HOST_NAME = 'testserver'

TEST_FIXTURE = FIXTURE_PATH / 'testing_fixture.json'

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class UtilsTestCase(TransactionTestCase):
    """
    """
    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """
        :return:
        """
        super(UtilsTestCase, self).setUp()
        self.request_factory = RequestFactory()
        self.user_model_cls = get_user_model()

    def test_get_group_key(self):
        """
        :return:
        """
        user = self.user_model_cls.objects.get(**{self.user_model_cls.USERNAME_FIELD: TEST_USER_NAME})
        request = self.request_factory.request(user=user)
        request.site = get_current_site(request)
        group = user.groups.all()[0]
        result = get_group_key(request, group)
        self.assertEqual(result, '%s_site_%s' % (get_cache_key(group.__hacs_base_content_type__, group), request.site.id))

    def test_get_user_key(self):
        """
        :return:
        """
        request = self.request_factory.request()
        request.user = user = self.user_model_cls.objects.get(**{self.user_model_cls.USERNAME_FIELD: TEST_USER_NAME})
        request.site = get_current_site(request)
        result = get_user_key(request)
        self.assertEqual(result, '%s_site_%s' % (
            get_cache_key(request.user.__hacs_base_content_type__, request.user), request.site.id))

    @override_settings(HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir())
    def test_get_generated_urlconf_file(self):
        """
        :return:
        """
        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingRules.objects.get(site=site)

        result = get_generated_urlconf_file(site_route.route.slug, prefix='hacs')
        self.assertEqual(result, '/tmp/hacs_%s_urls.py' % sanitize_filename(site_route.route.slug))

    @override_settings(HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir())
    def test_generate_urlconf_file(self):

        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingRules.objects.get(site=site)
        filename = get_generated_urlconf_file(site_route.route.slug, prefix='hacs')
        if os.path.exists(filename):
            os.unlink(filename)

        generate_urlconf_file(filename, site_route.route)
        self.assertTrue(os.path.exists(filename))
        # Clean generated
        os.unlink(filename)

    @override_settings(HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir())
    def test_get_generated_urlconf_module(self):

        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingRules.objects.get(site=site)
        filename = get_generated_urlconf_file(site_route.route.slug, prefix='hacs')
        generate_urlconf_file(filename, site_route.route)
        if tempfile.gettempdir() not in sys.path:
            sys.path.append(tempfile.gettempdir())
        result = get_generated_urlconf_module(filename, validation=True)
        self.assertEqual(result, 'hacs_default_route_urls')
        try:
            import_module(result)
        except ImportError:
            raise AssertionError("Code should not come here")
        # Clean Generated File
        os.unlink(filename)

    def test_sanitize_filename(self):

        dirty_name = "Mকy D@-^a~d. Mam"
        expected_name = "MyD_adMam"
        result = sanitize_filename(dirty_name)

        self.assertEqual(expected_name, result)

    def test_get_installed_apps_urlconf(self):

        results = get_installed_apps_urlconf()

        # As three apps have urls (url pattern)(django.contrib.auth, django.contrib.staticfiles, hacs)
        # So results should have length 3 but hacs has two urlconf so total should have 4
        self.assertEqual(4, len(results))

        hacs_urls = [x for x in results if x.app_label == 'hacs'][0]
        urlconf = import_module(hacs_urls.module)
        self.assertIsInstance(urlconf.urlpatterns, list)

        from django.core.urlresolvers import RegexURLPattern
        self.assertIsInstance(urlconf.urlpatterns[0], RegexURLPattern)

        # hacs urls has two custom handler
        self.assertEqual(2, len(hacs_urls.error_handlers))

        # Make sure exclude apps working
        results = get_installed_apps_urlconf(exclude=('staticfiles', ))
        self.assertEqual(3, len(results))

        # Make sure patterns work
        results = get_installed_apps_urlconf(r'fake')
        self.assertEqual(0, len(results))

        # Make sure json serializer works
        results = get_installed_apps_urlconf(to_json=True)
        self.assertIsInstance(results, six.string_types)

        # Make sure valid json string
        import json
        try:
            results = json.loads(results)
            self.assertEqual(4, len(results))
        except ValueError:
            raise AssertionError("Could should not come here! Most provably invalid json string")

__all__ = ['UtilsTestCase', ]
