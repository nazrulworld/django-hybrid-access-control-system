# -*- coding: utf-8 -*-
# ++ This file `admin.py` is generated at 6/14/16 6:23 AM ++
from __future__ import unicode_literals
import json
from django.utils import six
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


@staff_member_required()
def select2_users_view(request):
    """"""
    max_records = 500
    import ipdb;ipdb.set_trace()
    if request.method == 'GET':
        UserModel = get_user_model()
        if request.GET.get('pk'):
            fields_map = {'id': 'pk', 'text': UserModel.USERNAME_FIELD}
            user = UserModel.objects.get(pk=request.GET.get('pk'))
            if request.GET.get('fields_map'):
                if isinstance(request.GET.get('fields_map'), six.string_types):
                    fields_map = json.loads(request.GET.get('fields_map'))
            data = {k: getattr(user, v) for k, v in six.iteritems(fields_map)}
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
                filters[UserModel.USERNAME_FIELD + '__contains'] = term

            queryset = UserModel.objects.filter(**filters)
            data['total_count'] = len(queryset)
            data['items'] = [{"id": item.pk, "text": getattr(item, UserModel.USERNAME_FIELD)}
                             for item in queryset[offset:limit]]
            data['incomplete_results'] = False if data['items'] else True
        return JsonResponse(data=data)

    else:
        pass


@staff_member_required()
def select2_groups_view(request):
    """"""
    max_records = 50

    if request.method == 'GET':
        if request.GET.get('pk'):
            fields_map = {'id': 'pk', 'text': 'name'}
            user = Group.objects.get(pk=request.GET.get('pk'))
            if request.GET.get('fields_map'):
                if isinstance(request.GET.get('fields_map'), six.string_types):
                    fields_map = json.loads(request.GET.get('fields_map'))
            data = {k: getattr(user, v) for k, v in six.iteritems(fields_map)}
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
                filters['name__contains'] = term

            queryset = Group.objects.filter(**filters)
            data['total_count'] = len(queryset)
            data['items'] = [{"id": item.pk, "text": item.name}
                             for item in queryset[offset:limit]]
            data['incomplete_results'] = False if data['items'] else True
        return JsonResponse(data=data)

    else:
        pass

