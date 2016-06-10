# -*- coding: utf-8 -*-
# ++ This file `forms.py` is generated at 6/4/16 8:55 AM ++
from __future__ import unicode_literals
from django import forms

from .models import RoutingTable


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in ('RoutingTableForm', 'RoutingTableAdminForm', )]


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
