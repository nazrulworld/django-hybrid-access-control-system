# -*- coding: utf-8 -*-
# ++ This file `init_hacs.py` is generated at 5/16/16 1:16 PM ++

from django.utils import six
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from hacs.models import RoutingTable
from hacs.models import SiteRoutingRules

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

if six.PY2:
    input = raw_input

class Command(BaseCommand):
    """
    """
    help = "HACS: Command tool for initialize hacs environment"
    can_import_settings = True

    def add_arguments(self, parser):
        """
        :param parser:
        :return:
        """
        parser.add_argument(
            '-d',
            '--domain-name',
            action='store',
            dest='domain_name',
            help='Default domain name for site'
        )
        parser.add_argument(
            '-u',
            '--urlconf-module',
            action='store',
            dest='urlconf_module',
            help='urlconf module name, that will used at default route'
        )
        parser.add_argument(
            '-r',
            '--route-name',
            action='store',
            dest='route_name',
            default='default-route',
            help='Default route name'

        )

    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        if not get_user_model().objects.filter(is_superuser=True).exists():
            raise LookupError("Before Run This command, make sure a superuser is already created.")
        domain = options['domain_name']
        while True:
            if not domain:
                domain = input('Please provide domain name for site. [localhost]')
                if not domain:
                    domain = 'localhost'
            else:
                break

        urlconf = options['urlconf_module']
        while True:
            if not urlconf:
                urlconf = input('Please provide root urlconf [%s]' % settings.ROOT_URLCONF)
                if not urlconf:
                    urlconf = settings.ROOT_URLCONF
            else:
                break

        try:
            site = Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            site = Site(domain=domain, name=domain)
            site.save()

        try:
            route = RoutingTable.objects.get_by_natural_key(options['route_name'])
        except RoutingTable.DoesNotExist:
            route = RoutingTable(
                name=options['route_name'],
                slug=options['route_name'],
                urls=[
                    {
                        "prefix": None,
                        "url_module": urlconf,
                        "namespace": None,
                        "children": []
                    },
                ],
                handlers={
                    "handler400": "hacs.views.errors.bad_request",
                    "handler403": "hacs.views.errors.permission_denied",
                    "handler404": "hacs.views.errors.page_not_found",
                    "handler500": "hacs.views.errors.server_error"
                },
                created_by=get_user_model().objects.filter(is_superuser=True).first(),
            )
            route.save()

        SiteRoutingRules(
            name="%s-%s" % (site.domain, route.name),
            slug="%s-%s" % (site.domain, route.name),
            site=site,
            route=route,
            created_by=get_user_model().objects.filter(is_superuser=True).first()
        ).save()
        self.stdout.write('>>> Django Hybrid Access Control System is initialized and ready to use! <<<')


