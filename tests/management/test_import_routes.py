# -*- coding: utf-8 -*-
# ++ This file `test_management_import_routes.py` is generated at 4/12/16 7:32 PM ++
import os
import shutil
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.encoding import smart_text
from django.core.management import call_command
from django.core.management import CommandError
from django.contrib.contenttypes.models import ContentType

from hacs.models import HacsGroupModel
from hacs.models import RoutingTable
from hacs.models import SiteRoutingRules
from hacs.models import ContentTypeRoutingRules

from tests.path import FIXTURE_PATH

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

TEST_FIXTURE = FIXTURE_PATH / 'testing_fixture.json'
ROUTE_FIXTURE = FIXTURE_PATH / 'testing_routing_fixture.json'


class TestImportRoutes(TestCase):
    """ """
    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_model_cls = get_user_model()
        self.clean()

    def clean(self):
        """ Cleaning all existing Routing records those are comes with fixture """
        ContentTypeRoutingRules.objects.all().delete()
        SiteRoutingRules.objects.all().delete()
        RoutingTable.objects.all().delete()

    def test_with_source_file(self):
        """ """
        call_command('import_routes', source=smart_text(ROUTE_FIXTURE))
        _test_user = 'superuser@test.com'
        _test_group = 'Administrators'
        _test_site = 'testserver'

        # We just checking all entries are inserted from fixture
        self.assertEqual(4, len(RoutingTable.objects.all()))
        self.assertEqual(2, len(SiteRoutingRules.objects.all()))
        self.assertEqual(7, len(ContentTypeRoutingRules.objects.all()))

        site = Site.objects.get(domain=_test_site)
        self.assertIsNotNone(SiteRoutingRules.objects.get(site=site))
        self.assertIsNotNone(ContentTypeRoutingRules.objects.get(
            site=site,
            content_type=ContentType.objects.get_for_model(HacsGroupModel),
            object_id=HacsGroupModel.objects.get_by_natural_key(_test_group).pk
        ))
        self.assertIsNotNone(ContentTypeRoutingRules.objects.get(
            site=site,
            content_type=ContentType.objects.get_for_model(self.user_model_cls),
            object_id=self.user_model_cls.objects.get(**{self.user_model_cls.USERNAME_FIELD: _test_user}).pk
        ))

        self.clean()
        # Test: site exclude
        # Let's omit Site
        call_command('import_routes', source=smart_text(ROUTE_FIXTURE), exclude_sites=[_test_site])
        # Excluded site should not have any route
        try:
            SiteRoutingRules.objects.get(site=site)
            raise AssertionError("Code should not reach here!, because object should not exist")
        except SiteRoutingRules.DoesNotExist:
            pass

        # As 5 entries are ignored, because those were related to exclude site
        self.assertEqual(2, len(ContentTypeRoutingRules.objects.all()))

        self.clean()
        # Test: group exclude
        call_command('import_routes', source=smart_text(ROUTE_FIXTURE), exclude_groups=[_test_group])
        try:
            ContentTypeRoutingRules.objects.get(
                site=site,
                content_type=ContentType.objects.get_for_model(HacsGroupModel),
                object_id=HacsGroupModel.objects.get_by_natural_key(_test_group).pk
            )
            raise AssertionError("Code should not reach here!, because group object should not exist")
        except ContentTypeRoutingRules.DoesNotExist:
            pass

        # As 2 entries are ignored, because those were related to exclude group
        self.assertEqual(5, len(ContentTypeRoutingRules.objects.all()))

        self.clean()
        # Test: group exclude
        call_command('import_routes', source=smart_text(ROUTE_FIXTURE), exclude_users=[_test_user])
        try:
            ContentTypeRoutingRules.objects.get(
                site=site,
                content_type=ContentType.objects.get_for_model(self.user_model_cls),
                object_id=self.user_model_cls.objects.get(**{self.user_model_cls.USERNAME_FIELD: _test_user}).pk
            )
            raise AssertionError("Code should not reach here!, because object should not exist")
        except ContentTypeRoutingRules.DoesNotExist:
            pass

        # As 2 entries are ignored, because those were related to exclude user
        self.assertEqual(5, len(ContentTypeRoutingRules.objects.all()))

        self.clean()
        # Test: multi excluding
        call_command('import_routes', source=smart_text(ROUTE_FIXTURE), exclude_groups=_test_group, exclude_users=_test_user)
        # As 2 + 2 entries are ignored, because those were related to exclude user and group
        self.assertEqual(3, len(ContentTypeRoutingRules.objects.all()))

    def test_with_autodiscover_files(self):
        """"""
        HACS_SERIALIZED_ROUTE_DIR_NAME = tempfile.mkdtemp('fixture')

        with self.settings(HACS_SERIALIZED_ROUTING_DIR=HACS_SERIALIZED_ROUTE_DIR_NAME):
            # Copy Test Route Fixture to tmp directory
            shutil.copyfile(smart_text(ROUTE_FIXTURE), os.path.join(HACS_SERIALIZED_ROUTE_DIR_NAME, ROUTE_FIXTURE.parts[-1]))
            call_command('import_routes')
            # We just checking all entries are inserted from fixture
            self.assertEqual(4, len(RoutingTable.objects.all()))
            self.assertEqual(2, len(SiteRoutingRules.objects.all()))
            self.assertEqual(7, len(ContentTypeRoutingRules.objects.all()))

        shutil.rmtree(HACS_SERIALIZED_ROUTE_DIR_NAME)

    def test_exceptions(self):
        """"""
        _test_user = 'superuser@test.com'
        _test_group = 'Administrators'
        _test_site = 'testserver'
        _test_route1 = 'test-route1'
        # Test: validation error:: required param missing
        try:
            call_command('import_routes', omit_app_dir_walking=True)
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn("Required value is missing!", smart_text(exc))

        # Test: validation error:: invalid/not installed app provided
        try:
            call_command('import_routes', exclude_apps=['fake_app'])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid app', smart_text(exc))

        # Test: validation error:: invalid site name is provided
        try:
            call_command('import_routes', exclude_sites=[_test_site, 'fake_site', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_site', smart_text(exc))

        # Test: validation error:: invalid group name is provided
        try:
            call_command('import_routes', exclude_groups=[_test_group, 'fake_group', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_group', smart_text(exc))

        # Test: validation error:: invalid user name is provided
        try:
            call_command('import_routes', exclude_users=[_test_user, 'fake_user', ])
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('fake_user', smart_text(exc))

        # Test: with `source`, invalid app and path
        try:
            call_command('import_routes', source='fake_app:fake_file.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid app path pattern', smart_text(exc))

        # Test: with source, correct app but invalid path
        try:
            call_command('import_routes', source='hacs:fake_file.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid source path specified!', smart_text(exc))
        _temp_dir = tempfile.mkdtemp()
        shutil.copyfile(smart_text(TEST_FIXTURE), os.path.join(_temp_dir, 'test.json'))

        # Test: with `source` valid file but HACS_SERIALIZED_ROUTING_DIR is not set
        try:
            call_command('import_routes', source='test.json')
            raise AssertionError("Code should not reach here!, because of validation error")
        except CommandError as exc:
            self.assertIn('Invalid source path specified!', smart_text(exc))

        # Test: with `source` HACS_SERIALIZED_ROUTING_DIR is set but invalid file
        with self.settings(HACS_SERIALIZED_ROUTING_DIR=_temp_dir):
            try:
                call_command('import_routes', source='fake_test.json')
                raise AssertionError("Code should not reach here!, because of validation error")
            except CommandError as exc:
                self.assertIn('Invalid source path specified!', smart_text(exc))


    def tearDown(self):

        super(TestImportRoutes, self).tearDown()
