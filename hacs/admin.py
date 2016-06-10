# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin

from .models import RoutingTable
from .models import SiteRoutingTable
from .models import ContentTypeRoutingTable
from .defaults import HACS_DEVELOPMENT_MODE
from .forms import RoutingTableAdminForm

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


@admin.register(RoutingTable)
class RoutingTableAdmin(admin.ModelAdmin):
    """"""
    form = RoutingTableAdminForm

    class Media:
        css = {}
        if getattr(settings, 'HACS_DEVELOPMENT_MODE', HACS_DEVELOPMENT_MODE):
            css['all'] = (
                'hacs_assets/css/jquery-ui.css',
                'hacs_assets/css/jqueryui-editable.css',
                'hacs_assets/css/hacs.css',
            )
            # Why Own jQuery: https://docs.djangoproject.com/en/1.9/ref/contrib/admin/#jquery
            js = (
                'hacs_assets/js/lodash.4.13.1.js',
                'hacs_assets/js/jquery-2.2.4.js',
                'hacs_assets/js/jquery-ui.js',
                'hacs_assets/js/jqueryui-editable.js',
                'hacs_assets/js/hacs.js',
            )
        else:
            css['all'] = ('admin/hacs/css/hacs.min.css', )
            js = ("admin/hacs/js/hacs.min.js",)


@admin.register(SiteRoutingTable)
class SiteRoutingTableAdmin(admin.ModelAdmin):
    pass


@admin.register(ContentTypeRoutingTable)
class ContentTypeRoutingTableAdmin(admin.ModelAdmin):
    pass
