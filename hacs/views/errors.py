# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.defaults import page_not_found
from django.views.defaults import server_error
from django.views.defaults import bad_request
from django.views.defaults import permission_denied

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.translation import ugettext

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


ERROR_405_TEMPLATE_NAME = 'hacs/errors/405.html'
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
    if request.META.get('HTTP_ACCEPT'):
        if request.META.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.META.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.META.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 503,
            'reason': ugettext('Service is not available, maintenance in progress')
        }
        data['contents'] = None
        return JsonResponse(data=data, status=503, reason=data['meta']['reason'])
    data = render(request, ERROR_503_MAINTENANCE_MODE_TEMPLATE_NAME, data)

    return HttpResponse(content=data, status=503, reason=ugettext('service is not available, maintenance in progress'))


def service_unavailable(request):
    """"""
    data = {}
    json_response = False
    if request.META.get('HTTP_ACCEPT'):
        if request.META.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.META.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.META.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 503,
            'reason': ugettext('503: Service is not available.')
        }
        data['contents'] = None
        return JsonResponse(data=data, status=503, reason=data['meta']['reason'])

    data = render(request, ERROR_503_TEMPLATE_NAME, data)
    return HttpResponse(content=data, status=503, reason=ugettext('service is not available'))


def http_method_not_permitted(request):
    """"""
    data = {}
    json_response = False
    if request.META.get('HTTP_ACCEPT'):
        if request.META.get('HTTP_ACCEPT').lower().split(',')[0].strip() in JSON_CONTENT_TYPES:
            json_response = True
    elif request.is_ajax() and not request.META.get('HTTP_ACCEPT'):
        json_response = True
    elif request.is_ajax() and 'text/html' not in request.META.get('HTTP_ACCEPT').lower():
        json_response = True

    if json_response:
        data['meta'] = {
            'status': 405,
            'reason': ugettext('%s HTTP method is not permitted' % request.method)
        }
        data['contents'] = None
        return JsonResponse(data=data, status=405, reason=data['meta']['reason'])

    data['current_http_method'] = request.method
    data = render(request, ERROR_405_TEMPLATE_NAME, data)
    return HttpResponse(content=data, status=405, reason=ugettext('method is not permitted'))
