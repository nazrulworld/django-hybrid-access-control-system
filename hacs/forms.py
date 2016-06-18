# -*- coding: utf-8 -*-
# ++ This file `forms.py` is generated at 6/4/16 8:55 AM ++
from __future__ import unicode_literals
from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import RoutingTable
from .models import ContentTypeRoutingTable


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in ('RoutingTableForm', 'RoutingTableAdminForm', 'ContentTypeRoutingTableForm',
                            'ContentTypeRoutingTableAdminForm')]


class RoutingTableForm(forms.ModelForm):
    """"""
    class Meta:
        model = RoutingTable
        fields = ('route_name', 'description', 'urls', 'handlers', 'allowed_method', 'is_active', )
        widgets = {
            'allowed_method': forms.SelectMultiple()
        }


class RoutingTableAdminForm(RoutingTableForm):
    """"""

    class Meta(RoutingTableForm.Meta):
        model = None


class ContentTypeRoutingTableForm(forms.ModelForm):
    """"""
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.filter(
        model__in=("user", "group", ),
        app_label__in=("auth", )
    ))

    class Meta:
        model = ContentTypeRoutingTable
        fields = ('route', 'site', 'content_type', 'object_id', 'is_active',)


class ContentTypeRoutingTableAdminForm(ContentTypeRoutingTableForm):
    """"""
    class Meta(ContentTypeRoutingTableForm.Meta):
        model = None
