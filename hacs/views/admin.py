# -*- coding: utf-8 -*-
# ++ This file `admin.py` is generated at 6/14/16 6:23 AM ++
from __future__ import unicode_literals
import json
from django.utils import six
from django.http import JsonResponse
from django.utils.translation import ugettext
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


@staff_member_required()
def select2_contenttypes_view(request, content_type):
    """
    :param request:
    :param content_type:
    :return:
    @TODO: depends on HTTP_ACCEPT  html or json could be returned, for case of html only
    collection of <option value=""></option> will be returned

    """
    UserModel = get_user_model()
    max_records = 500
    content_types = {
        'user': {
            'model': UserModel,
            'searchable': UserModel.USERNAME_FIELD,
            'fields_map': {'id': 'pk', 'text': UserModel.USERNAME_FIELD}
        },
        'group': {
            'model': Group,
            'searchable': "name",
            'fields_map': {'id': 'pk', 'text': "name"}
        }
    }
    try:
        content_type_conf = content_types[content_type]
    except KeyError:
        raise

    if request.method == 'GET':

        if request.GET.get('pk'):
            fields_map = content_type_conf['fields_map'].copy()
            try:
                content_object = content_type_conf['model'].objects.get(pk=request.GET.get('pk'))
            except content_type_conf['model'].DoesNotExist:
                return JsonResponse({
                    "meta": {
                        "status": 500,
                        "reason": ugettext("no user found corresponded to PK `%s`." % request.GET.get('pk'))
                    }
                }, status=500)

            if request.GET.get('fields_map'):
                if isinstance(request.GET.get('fields_map'), six.string_types):
                    fields_map = json.loads(request.GET.get('fields_map'))
            data = {k: getattr(content_object, v) for k, v in six.iteritems(fields_map)}
        else:
            if request.GET.get('max_records'):
                max_records = int(request.GET.get('max_records'))
            page = int(request.GET.get('page', 1))
            if page == 0:
                page = 1
            term = request.GET.get('q', None)
            offset = 0 if page == 1 else (page - 1) * max_records
            limit = page * max_records
            data = {}
            filters = dict()
            if term:
                filters[content_type_conf['searchable'] + '__contains'] = term

            queryset = content_type_conf['model'].objects.filter(**filters)
            data['total_count'] = len(queryset)
            data['items'] = [{k: getattr(item, v) for k, v in six.iteritems(content_type_conf['fields_map'])}
                             for item in queryset[offset:limit]]
            data['incomplete_results'] = False if data['items'] else True
        return JsonResponse(data=data)

    else:
        data = {
            "meta": {
                "status": 405,
                "reason": ugettext("only GET is permitted!")
            }
        }
        return JsonResponse(data=data, status=405, reason=ugettext("only GET is permitted!"))
