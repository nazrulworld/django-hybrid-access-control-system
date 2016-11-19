# -*- coding: utf-8 -*-
# ++ This file `test_validators.py` is generated at 6/28/16 1:32 PM ++
import os
import sys
import copy
import json
import tempfile
from django.conf import settings
from django.test import TestCase
from django.test import override_settings
from django.core.validators import ValidationError
from django.utils.encoding import smart_text
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType


from hacs.models import RoutingTable
from hacs.models import HacsGroupModel
from hacs.validators import UrlModulesValidator
from hacs.validators import HttpHandlerValidator
from hacs.validators import ContentTypeValidator
from hacs.utils import generate_urlconf_file_on_demand

from .path import FIXTURE_PATH

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

if tempfile.gettempdir() not in sys.path:
    sys.path.append(tempfile.gettempdir())


TEST_USER_NAME = 'test_user'
TEST_ROUTE = "default-route"

TEST_FIXTURE = FIXTURE_PATH / 'testing_fixture.json'


@override_settings(HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir())
class TestUrlModulesValidator(TestCase):
    """
    """
    fixtures = (TEST_FIXTURE,)

    def test_valid(self):
        """"""
        validator = UrlModulesValidator()
        result = validator(None)
        # No Values should be pass
        self.assertIsNone(result)
        route = RoutingTable.objects.get(route_name=TEST_ROUTE)
        generate_urlconf_file_on_demand(route)
        try:
            validator(route.urls)
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        try:
            validator(smart_text(route.urls))
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        try:
            validator(json.dumps(route.urls))
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        # Test equal to
        validator2 = UrlModulesValidator()
        assert validator == validator2, "two instances must be equal"
        # Test not equal
        validator2.message = "my custom message"
        assert validator2 != validator, "two instances must not be equal"

    def test_invalid(self):
        """"""
        validator = UrlModulesValidator()
        try:
            validator('Invalid JSON and Invalid python eval value')
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError as exc:
            self.assertIn('Invalid JSON and Invalid python eval value', smart_text(exc))

        route = RoutingTable.objects.get(route_name=TEST_ROUTE)
        # Test invalid data type
        try:
            validator({'fake': route.urls})
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        try:
            validator(json.dumps({'fake': route.urls}))
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        try:
            validator(smart_text({'fake': route.urls}))
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        # Test Invalid python module
        urls = copy.copy(route.urls)
        urls[0].update({'url_module': 'fake_module'})
        try:
            validator(urls)
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError as exc:
            self.assertIn('Invalid url module `fake_module`', smart_text(exc))

        # Test valid python module but not valid urlconf module
        urls[0].update({'url_module': 'hacs.views.errors'})
        try:
            validator(urls)
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError as exc:
            self.assertIn('url module `hacs.views.errors`', smart_text(exc))

    def tearDown(self):
        """
        :return:
        """
        super(TestUrlModulesValidator, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))


@override_settings(HACS_GENERATED_URLCONF_DIR=tempfile.gettempdir())
class TestHttpHandlerValidator(TestCase):
    """
    """
    fixtures = (TEST_FIXTURE,)

    def test_valid(self):
        """"""
        validator = HttpHandlerValidator()
        result = validator(None)
        # No Values should be pass
        self.assertIsNone(result)
        route = RoutingTable.objects.get(route_name=TEST_ROUTE)
        generate_urlconf_file_on_demand(route)
        try:
            validator(route.handlers)
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        try:
            validator(smart_text(route.handlers))
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        try:
            validator(json.dumps(route.handlers))
        except ValidationError as exc:
            raise AssertionError("Code should not come here, as should pass. Original error: %s" % smart_text(exc))

        # Test equal to
        validator2 = HttpHandlerValidator()
        assert validator == validator2, "two instances must be equal"
        # Test not equal
        validator2.message = "my custom message"
        assert validator2 != validator, "two instances must not be equal"

    def test_invalid(self):
        """"""
        validator = HttpHandlerValidator()
        try:
            validator('Invalid JSON and Invalid python eval value')
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError as exc:
            self.assertIn('Invalid JSON and Invalid python eval value', smart_text(exc))

        route = RoutingTable.objects.get(route_name=TEST_ROUTE)
        # Test invalid data type
        try:
            validator((route.handlers, ))
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        try:
            validator(json.dumps((route.handlers, )))
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        try:
            validator(smart_text((route.handlers, )))
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        # Test Invalid python module
        handlers = route.handlers.copy()

        handlers.update({'403': 'fake_module'})
        try:
            validator(handlers)
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError as exc:
            self.assertIn('Invalid handler! fake_module', smart_text(exc))

    def tearDown(self):
        """
        :return:
        """
        super(TestHttpHandlerValidator, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))


class TestContentTypeValidator(TestCase):
    """"""
    fixtures = (TEST_FIXTURE, )

    def test_valid(self):
        """"""
        validator = ContentTypeValidator()
        # Test with User Content Type
        content_type = ContentType.objects.get_for_model(get_user_model())

        try:
            validator(content_type.pk)
        except ValidationError:
            raise AssertionError("Code should not come here, because should be valid")

        # Test with User Content Type
        content_type = ContentType.objects.get_for_model(HacsGroupModel)
        try:
            validator(content_type.pk)
        except ValidationError:
            raise AssertionError("Code should not come here, because should be valid")

        # We make sure white list works
        validator.white_list += (("sites", "site"), )

        # Test with User Content Type
        content_type = ContentType.objects.get_for_model(Site)
        try:
            validator(content_type.pk)
        except ValidationError:
            raise AssertionError("Code should not come here, because should be valid")

        # Test equal to
        validator2 = ContentTypeValidator()
        # Test not equal: should not equal because we change white list
        assert validator2 != validator, "two instances must not be equal"

        # should be equal now
        validator2.white_list += (("sites", "site"),)
        assert validator == validator2, "two instances must be equal"

    def test_invalid(self):
        """"""
        validator = ContentTypeValidator()
        # Test with User Content Type
        content_type = ContentType.objects.get_for_model(Site)
        try:
            validator(content_type.pk)
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass

        # Make sure blacklisted works as well
        validator.black_list = (("hacs", "hacsusermodel"), )
        content_type = ContentType.objects.get_for_model(get_user_model())
        try:
            validator(content_type.pk)
            raise AssertionError("Code should not come here, because of invalidation")
        except ValidationError:
            pass
