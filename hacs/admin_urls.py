# -*- coding: utf-8 -*-
# ++ This file `admin_urls.py` is generated at 6/15/16 6:25 PM ++
from __future__ import unicode_literals
from django.conf.urls import url
from .views.admin import select2_contenttypes_view

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

urlpatterns = [
    url(r'^select2\-(?P<content_type>[a-z]+)\-list/$',
        name='select2_contenttypes_list', view=select2_contenttypes_view)
]

handler403 = "hacs.views.errors.permission_denied"
handler404 = "hacs.views.errors.page_not_found"
