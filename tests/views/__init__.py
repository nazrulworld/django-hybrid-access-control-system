# -*- coding: utf-8 -*-
# ++ This file `__init__.py.py` is generated at 6/29/16 8:25 PM ++
from django.http import HttpResponse
from hacs.decorators import permission_required
from hacs.security.helpers import HACS_PORTAL_MANAGER_PERMISSION

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


@permission_required('hacs.PublicView')
def public_view(request):
    """
    :param request:
    :return:
    """
    return HttpResponse(b"<h1>Public View(Guest Can View)</h1>")


@permission_required('hacs.AuthenticatedView')
def authenticated_view(request):
    """
    :param request:
    :return:
    """
    return HttpResponse(b'<h1>Authenticated View</h1>')


@permission_required('hacs.ManageContent')
def content_manager_view(request):
    """
    :param request:
    :return:
    """
    return HttpResponse(b"<h1>Content Manager View</h1>")


@permission_required(HACS_PORTAL_MANAGER_PERMISSION)
def portal_manager_view(request):
    """
    :param request:
    :return:
    """
    return HttpResponse(b"<h1>Portal Manager View</h1>")
