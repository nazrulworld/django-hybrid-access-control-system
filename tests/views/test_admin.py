# -*- coding: utf-8 -*-
# ++ This file `test_admin.py` is generated at 6/29/16 8:25 PM ++
from __future__ import unicode_literals
import os
import json
import tempfile
from django.utils.http import urlencode
from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.core.cache import caches
from django.test import override_settings
from django.test import modify_settings
from django.core.urlresolvers import reverse
from django.utils.six.moves import range
from django.utils.encoding import smart_text
from django.test import RequestFactory
from hacs.views.admin import select2_contenttypes_view
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model

from hacs.utils import get_user_object
from hacs.globals import HACS_SITE_CACHE
from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.models import HacsGroupModel

from tests.path import FIXTURE_PATH
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

TEST_USER_NAME = 'superuser@test.com'
TEST_USER_PASSWORD = 'top_secret'
TEST_ROUTE = "default-route"
TEST_SITE = "testserver"

TEST_FIXTURE = FIXTURE_PATH / 'testing_fixture.json'


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
        # we have 5 users only
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 5)

        # Make sure Group Content Type works and we have 4 groups in total
        response = select2_contenttypes_view(request, 'group')
        self.assertEqual(json.loads(smart_text(response.content))['total_count'], 4)

        # Make sure filter works
        request.META['QUERY_STRING'] = urlencode({
                'q': 'member',
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
                email="nazrul_%s@fake.com" % x,
                password="nazrul_%s" % x
            )
        # existing 5 + 58
        self.assertEqual(63, len(get_user_model().objects.all()))

        request.META['QUERY_STRING'] = urlencode({
            'q': '',
            'max_records': 50,
            'page': 1
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['total_count'], 63)
        self.assertEqual(50, len(content['items']))

        request.META['QUERY_STRING'] = urlencode({
            'q': '',
            'max_records': 50,
            'page': 2
        }, doseq=True)
        del request.GET
        response = select2_contenttypes_view(request, 'user')
        content = json.loads(smart_text(response.content))
        # Second Page should have only 13 items
        self.assertEqual(13, len(content['items']))

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
            'pk': HacsGroupModel.objects.get_by_natural_key('Administrators').pk
        }, doseq=True)
        del request.GET

        response = select2_contenttypes_view(request, 'group')
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['text'], 'Administrators')

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

    def setUp(self):
        """"""
        super(TestSelect2ContentTypesViewFromBrowser, self).setUp()
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        self.fix_password()
        HACS_SITE_CACHE.clear()

    def fix_password(self):
        """
        :return:
        """
        from django.contrib.auth.hashers import is_password_usable
        for user in get_user_model().objects.all():
            if not is_password_usable(user.password):
                user.set_password(user.password)
                user.save()

    def test_view(self):
        """"""
        _url = reverse('hacs:select2_contenttypes_list', kwargs={"content_type": "user"})
        browser = Client()
        response = browser.get(_url)
        # Make sure authentication is required
        self.assertEqual(302, response.status_code)
        browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        # @TODO: need to full coverage
        response = browser.get(_url)
        # we have five users
        self.assertEqual(5, len(json.loads(smart_text(response.content))['items']))
        response = browser.get(reverse('hacs:select2_contenttypes_list', kwargs={"content_type": "group"}))
        # we should have 4 groups
        self.assertEqual(4, len(json.loads(smart_text(response.content))['items']))

        response = browser.get(reverse('hacs:select2_contenttypes_list', kwargs={"content_type": "group"}),
                               data={'q': "admin"})
        # we should have 1 group matched
        self.assertEqual(1, len(json.loads(smart_text(response.content))['items']))

        response = browser.get(_url, data={'q': "naz"})
        # we don't have any user name that contains naz
        self.assertEqual(0, len(json.loads(smart_text(response.content))['items']))
        self.assertTrue(json.loads(smart_text(response.content))['incomplete_results'])

        # Test: pagination
        for x in range(1, 59):
            get_user_model().objects.create_user(
                first_name="Nazrul_%s" % x,
                email="nazrul_%s@fake.com" % x,
                password="nazrul_%s" % x
            )
        # exiting 5 + 58 = 63
        self.assertEqual(63, len(get_user_model().objects.all()))

        response = browser.get(_url, data={"max_records": 50})
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['total_count'], 63)
        self.assertEqual(50, len(content['items']))

        response = browser.get(_url, data={"max_records": 50, "page": 2})
        content = json.loads(smart_text(response.content))
        # should 13 record in second page
        self.assertEqual(13, len(content['items']))

        # Test Single Record
        response = browser.get(_url, data={"pk": get_user_model().objects.get(**{get_user_model().USERNAME_FIELD: TEST_USER_NAME}).pk})
        content = json.loads(smart_text(response.content))
        self.assertEqual(content['id'], get_user_model().objects.get(**{get_user_model().USERNAME_FIELD: TEST_USER_NAME}).pk)

    def test_exception(self):
        """"""
        _url = reverse('hacs:select2_contenttypes_list', kwargs={"content_type": "user"})
        browser = Client()
        browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        response = browser.get(_url, data={"pk": 999})
        self.assertEqual(500, response.status_code)
        self.assertEqual(500, json.loads(smart_text(response.content))['meta']['status'])
        response = browser.post(_url, {"page": 1})
        self.assertEqual(405, response.status_code)


    def tearDown(self):
        """
        :return:
        """
        super(TestSelect2ContentTypesViewFromBrowser, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))

        HACS_SITE_CACHE.clear()
        self.cache.clear()
