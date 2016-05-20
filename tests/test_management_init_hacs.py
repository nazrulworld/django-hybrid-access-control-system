# -*- coding: utf-8 -*-
# ++ This file `test_management_init_hacs.py` is generated at 5/17/16 4:48 PM ++
import os
from django.test import TestCase
from django.contrib.sites.models import Site
from django.core.management import call_command

from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class TestInitHACS(TestCase):
    """ """

    def setUp(self):

        super(TestInitHACS, self).setUp()

    def clean(self):
        """ Cleaning all existing Routing records those are comes with fixture """
        SiteRoutingTable.objects.all().delete()
        RoutingTable.objects.all().delete()

    def test_handle(self):
        """ """

        call_command('init_hacs', domain_name='localhost', urlconf_module='hacs.urls', route_name='default-route')

        # we make sure HACS is initialized
        try:
            RoutingTable.objects.get_by_natural_key('default-route')
        except RoutingTable.DoesNotExist:
            raise AssertionError("Code should come here!, cause route should be created")

        try:
            site_route = SiteRoutingTable.objects.get(site=Site.objects.get(domain='localhost'))
            self.assertEqual(site_route.route.route_name, 'default-route')

        except SiteRoutingTable.DoesNotExist:
            raise AssertionError("Code should come here!, cause site route should be created")

    def tearDown(self):

        super(TestInitHACS, self).tearDown()
