# -*- coding: utf-8 -*-
# ++ This file `test_admin.py` is generated at 6/29/16 8:25 PM ++
import os
import json
import tempfile
from django.utils.http import urlencode
from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.test import override_settings
from django.test import modify_settings
from django.core.urlresolvers import reverse
from django.utils.six.moves import range
from django.utils.encoding import smart_text
from django.test import RequestFactory
from django.contrib.auth.models import Group
from hacs.views.admin import select2_contenttypes_view
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model

from hacs.utils import get_user_object
from hacs.models import SiteRoutingRules

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

TEST_USER_NAME = 'test_user'
TEST_USER_PASSWORD = 'top_secret'
TEST_ROUTE = "default-route"
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_FIXTURE = os.path.join(os.path.dirname(CURRENT_PATH), 'fixtures', 'testing_fixture.json')


class TestSelect2ContentTypesView(TestCase):
    """"""
    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """"""
        super(TestSelect2ContentTypesView, self).setUp()
        self.request_factory = RequestFactory()

    def test_view(self):
        """"""
        request = self.request_factory.request(
            QUERY_STRING=urlencode({
                'q': '',
                'max_records' : 50,
                'page': 1
            }, doseq=True)
        )
        request.site = get_current_site(request)
        request.user = get_user_object(TEST_USER_NAME)

        response = select2_contenttypes_view(request, 'user')
        self.assertEqual(response.status_code, 200)
        # we have two users only
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 2)

        # Make sure Group Content Type works and we have 3 groups in total
        response = select2_contenttypes_view(request, 'group')
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 3)

        # Make sure filter works
        request.META['QUERY_STRING'] = urlencode({
                'q': 'test_user_normal',
                'max_records' : 50,
                'page': 1
            }, doseq=True)
        # Invalid Cache Property: http://goo.gl/8HzxCd
        del request.GET
        response = select2_contenttypes_view(request, 'user')
        # should have one user only because of filter
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 1)

        # Make sure filter works for Group content type
        request.META['QUERY_STRING'] = urlencode({
            'q': 'admin',
            'max_records': 50,
            'page': 1
        }, doseq=True)
        del request.GET
        response = select2_contenttypes_view(request, 'group')
        # should have one user only because of filter
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 1)

        request.META['QUERY_STRING'] = urlencode({
            'q': 'naz',
            'max_records': 50,
            'page': 1
        }, doseq=True)
        del request.GET
        # should have zero user as no username contains naz
        response = select2_contenttypes_view(request, 'user')
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 0)

        # Test: pagination
        for x in range(1, 59):

            get_user_model().objects.create_user(
                first_name="Nazrul_%s" % x,
                username="nazrulworld_%s" % x,
                email="nazrul_%s@fake.com" % x,
                password="nazrul_%s" % x
            )

        self.assertEqual(60, len(get_user_model().objects.all()))

        request.META['QUERY_STRING'] = urlencode({
            'q': '',
            'max_records': 50,
            'page': 1
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['total_count'], 60)
        self.assertEqual(50, len(content['items']))

        request.META['QUERY_STRING'] = urlencode({
            'q': '',
            'max_records': 50,
            'page': 2
        }, doseq=True)
        del request.GET
        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        # Second Page should have only 10 items
        self.assertEqual(10, len(content['items']))

        request.META['QUERY_STRING'] = urlencode({
            'q': '',
            'max_records': 50,
            'page': 3
        }, doseq=True)
        del request.GET
        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))

        self.assertEqual(0, len(content['items']))
        self.assertTrue(content['incomplete_results'])

        # Test: for single entry
        request.META['QUERY_STRING'] = urlencode({
            'pk': request.user.pk
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['id'], request.user.pk)
        self.assertEqual(content['text'], TEST_USER_NAME)

        # Test: for single entry for Group content type
        request.META['QUERY_STRING'] = urlencode({
            'pk': Group.objects.get_by_natural_key('administrator').pk
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'group')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['text'], 'administrator')

        # Test: for single entry: with custom mapping
        request.META['QUERY_STRING'] = urlencode({
            'pk': request.user.pk,
            'fields_map': json.dumps({'text': 'email'})
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['text'], request.user.email)

    def test_view_exception(self):
        """"""
        request = self.request_factory.request()
        request.site = get_current_site(request)
        request.user = get_user_object(TEST_USER_NAME)
        request.META['QUERY_STRING'] = urlencode({
            'pk': '999'
        }, doseq=True)

        response = select2_contenttypes_view(request, 'user')
        # Should be http code server error as user is not exists
        self.assertEqual(500, response.status_code)
        self.assertEqual(500, json.loads(smart_text(response.content))['meta']['status'])

        request.method = 'POST'
        response = select2_contenttypes_view(request, 'user')
        # Should be http code not permitted
        self.assertEqual(405, response.status_code)
        self.assertEqual(405, json.loads(smart_text(response.content))['meta']['status'])

        # Test: authorization
        request.user.is_superuser = False
        request.user.is_staff = False
        request.user.save()
        request.method = 'GET'
        response = select2_contenttypes_view(request, 'user')
        # Should Be Redirect to login page
        self.assertEqual(302, response.status_code)
        self.assertIn('admin/login', response.url)


@modify_settings(MIDDLEWARE_CLASSES={'append': [
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'hacs.middleware.DynamicRouteMiddleware',
    'hacs.middleware.FirewallMiddleware'

]})
@override_settings(
    HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir(),
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'hacs_middleware',}},
)
class TestSelect2ContentTypesViewFromBrowser(TestCase):
    """"""
    fixtures = (TEST_FIXTURE, )

    def test_view(self):
        """"""
        request = RequestFactory().request()
        site = get_current_site(request)
        site_rules = SiteRoutingRules.objects.get(site=site)
        site_rules.route.urls.append({
            "prefix": "hacs",
            "url_module": "hacs.admin_urls",
            "app_name": "hacs",
            "namespace": "hacs_admin"
        })
        site_rules.route.save()
        browser = Client()
        browser.get('/admin/')
        browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        # @TODO: need to full coverage

    def tearDown(self):
        """
        :return:
        """
        super(TestSelect2ContentTypesViewFromBrowser, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))
