# -*- coding: utf-8 -*-
# ++ This file `forms.py` is generated at 6/4/16 8:55 AM ++
from __future__ import unicode_literals
from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import RoutingTable
from .models import ContentTypeRoutingRules


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in ('RoutingTableForm', 'RoutingTableAdminForm', 'ContentTypeRoutingRulesForm',
                            'ContentTypeRoutingRulesAdminForm', 'SiteRoutingRulesForm', 'SiteRoutingRulesAdminForm')]


class RoutingTableForm(forms.ModelForm):
    """"""
    class Meta:
        model = RoutingTable
        fields = ('route_name', 'description', 'urls', 'handlers', 'is_active', )


class RoutingTableAdminForm(RoutingTableForm):
    """"""

    class Meta(RoutingTableForm.Meta):
        model = None


class SiteRoutingRulesForm(forms.ModelForm):
    """"""
    class Meta:
        model = ContentTypeRoutingRules
        fields = ('route', 'site', 'allowed_method', 'is_active', 'blacklisted_uri',
                  'whitelisted_uri',
                  'maintenance_mode')
        widgets = {
            'allowed_method': forms.SelectMultiple()
        }


class SiteRoutingRulesAdminForm(SiteRoutingRulesForm):
    """"""
    class Meta(SiteRoutingRulesForm.Meta):
        model = None


class ContentTypeRoutingRulesForm(forms.ModelForm):
    """"""
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.filter(
        model__in=("user", "group", ),
        app_label__in=("auth", )
    ))

    class Meta:
        model = ContentTypeRoutingRules
        fields = ('route', 'site', 'content_type', 'allowed_method', 'object_id', 'is_active', 'blacklisted_uri',
                  'whitelisted_uri', 'maintenance_mode')
        widgets = {
            'allowed_method': forms.SelectMultiple()
        }


class ContentTypeRoutingRulesAdminForm(ContentTypeRoutingRulesForm):
    """"""
    class Meta(ContentTypeRoutingRulesForm.Meta):
        model = None
