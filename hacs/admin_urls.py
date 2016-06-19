# -*- coding: utf-8 -*-
# ++ This file `admin_urls.py` is generated at 6/15/16 6:25 PM ++
from __future__ import unicode_literals
from django.conf.urls import url

from .views.admin import select2_users_view
from .views.admin import select2_groups_view

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

urlpatterns = [
    url(r'^admin/select2\-users/$', name='select2_users', view=select2_users_view),
    url(r'^admin/select2\-groups/$', name='select2_groups', view=select2_groups_view)
]

handler403 = "hacs.views.errors.permission_denied"
handler404 = "hacs.views.errors.page_not_found"
