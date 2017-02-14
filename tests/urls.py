# -*- coding: utf-8 -*-
# ++ This file `urls.py` is generated at 2/13/17 7:46 PM ++
from django.conf.urls import url
from tests.views import public_view, authenticated_view, portal_manager_view, content_manager_view

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

urlpatterns = [
    url(r'^$', name='public_view', view=public_view),
    url(r'^authenticated-view/$', name='authenticated_view', view=authenticated_view),
    url(r'^portal-manager-view/$', name='portal_manager_view', view=portal_manager_view),
    url(r'^content-manager-view/$', name='content_manager_view', view=content_manager_view),
]

handler403 = "hacs.views.errors.permission_denied"
handler404 = "hacs.views.errors.page_not_found"
