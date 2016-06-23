# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.defaults import page_not_found
from django.views.defaults import server_error
from django.views.defaults import bad_request
from django.views.defaults import permission_denied

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in (
    'page_not_found',
    'server_error',
    'bad_request',
    'permission_denied',
    'maintenance_mode',
    'service_unavailable',
    'http_method_not_permitted'
)]


ERROR_405_TEMPLATE_NAME = '405.html'
ERROR_404_TEMPLATE_NAME = '404.html'
ERROR_403_TEMPLATE_NAME = '403.html'
ERROR_400_TEMPLATE_NAME = '400.html'
ERROR_500_TEMPLATE_NAME = '500.html'
ERROR_503_TEMPLATE_NAME = 'hacs/errors/503.html'
ERROR_503_MAINTENANCE_MODE_TEMPLATE_NAME = 'hacs/errors/503_maintenance_mode.html'
JSON_CONTENT_TYPES = (
    'application/json',
    'text/json'
)


def maintenance_mode(request):
    """"""
    data = {}
    json_response = False
    if request.meta.get('HTTP_ACCEPT'):
        if request.meta.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.meta.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.meta.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 503,
            'reason': _('Service is not available, maintenance in progress')
        }
        data['contents'] = None
        return JsonResponse(data=data)

    return TemplateResponse(request, ERROR_503_TEMPLATE_NAME, data, status=503)


def service_unavailable(request):
    """"""
    data = {}
    json_response = False
    if request.meta.get('HTTP_ACCEPT'):
        if request.meta.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.meta.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.meta.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 503,
            'reason': _('503: Service is not available.')
        }
        data['contents'] = None
        return JsonResponse(data=data)

    return TemplateResponse(request, ERROR_503_TEMPLATE_NAME, data, status=503)


def http_method_not_permitted(request):
    """"""
    data = {}
    json_response = False
    if request.meta.get('HTTP_ACCEPT'):
        if request.meta.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.meta.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.meta.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 405,
            'reason': _('%s HTTP method is not permitted' % request.method)
        }
        data['contents'] = None
        return JsonResponse(data=data)

    data['current_http_method'] = request.method
    return TemplateResponse(request, ERROR_405_TEMPLATE_NAME, data, status=405)
