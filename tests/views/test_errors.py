# -*- coding: utf-8 -*-
# ++ This file `test_errors.py` is generated at 6/29/16 8:25 PM ++
import os
import json
import tempfile
from django.utils.encoding import smart_text
from django.test import TestCase
from django.test import RequestFactory
from django.test import override_settings
from django.test import modify_settings
from django.http import Http404

from hacs.views.errors import *
from hacs.views.errors import ERROR_403_TEMPLATE_NAME
from hacs.views.errors import ERROR_404_TEMPLATE_NAME
from hacs.views.errors import ERROR_500_TEMPLATE_NAME
from hacs.views.errors import ERROR_400_TEMPLATE_NAME
from hacs.views.errors import ERROR_503_MAINTENANCE_MODE_TEMPLATE_NAME

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_FIXTURE = os.path.join(os.path.dirname(CURRENT_PATH), 'fixtures', 'testing_fixture.json')


class TestPageNotFound(TestCase):
    """"""

    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        response = page_not_found(request, Http404("page not found"), ERROR_404_TEMPLATE_NAME)
        self.assertEqual(404, response.status_code)
        self.assertIn('not found', smart_text(response.content).lower())


class TestServerError(TestCase):
    """"""

    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        response = server_error(request, ERROR_500_TEMPLATE_NAME)
        self.assertEqual(500, response.status_code)
        self.assertIn('server error', smart_text(response.content).lower())


class TestBadRequest(TestCase):
    """"""

    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        response = bad_request(request, Exception('bad request'), ERROR_400_TEMPLATE_NAME)
        self.assertEqual(400, response.status_code)
        self.assertIn('bad request', smart_text(response.content).lower())


class TestPermissionDenied(TestCase):
    """"""

    fixtures = (TEST_FIXTURE,)

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        response = permission_denied(request, Exception('403 forbidden'), ERROR_403_TEMPLATE_NAME)
        self.assertEqual(403, response.status_code)
        self.assertIn('403 forbidden', smart_text(response.content).lower())


class TestMaintenanceMode(TestCase):
    """"""

    fixtures = (TEST_FIXTURE,)

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        request.META['HTTP_ACCEPT'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        response = maintenance_mode(request)
        self.assertEqual(503, response.status_code)
        self.assertIn('503', smart_text(response.content))

        request.META['HTTP_ACCEPT'] = "application/json, text/javascript, */*; q=0.01"
        response = maintenance_mode(request)
        try:
            content = json.loads(smart_text(response.content))
            self.assertEqual(503, content['meta']['status'])
        except ValueError:
            raise AssertionError("Could should not come here.")


class TestServiceUnavailable(TestCase):
    """"""

    fixtures = (TEST_FIXTURE,)

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        request.META['HTTP_ACCEPT'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        response = service_unavailable(request)
        self.assertEqual(503, response.status_code)
        self.assertIn('503', smart_text(response.content))

        request.META['HTTP_ACCEPT'] = "application/json, text/javascript, */*; q=0.01"
        response = service_unavailable(request)
        try:
            content = json.loads(smart_text(response.content))
            self.assertEqual(503, content['meta']['status'])
        except ValueError:
            raise AssertionError("Could should not come here.")


class TestHttpMethodNotPermitted(TestCase):
    """"""

    fixtures = (TEST_FIXTURE,)

    def setUp(self):
        """"""
        self.request_factory = RequestFactory()

    def test_view(self):
        """
        :return:
        """
        request = self.request_factory.request()
        request.META['HTTP_ACCEPT'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        request.method = 'PUT'
        response = http_method_not_permitted(request)
        self.assertEqual(405, response.status_code)
        self.assertIn('PUT method', smart_text(response.content))

        request.META['HTTP_ACCEPT'] = "application/json, text/javascript, */*; q=0.01"
        response = http_method_not_permitted(request)
        try:
            content = json.loads(smart_text(response.content))
            self.assertEqual(405, content['meta']['status'])
        except ValueError:
            raise AssertionError("Could should not come here.")
