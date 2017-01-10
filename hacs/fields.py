# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ++ This file `fields.py` is generated at 3/4/16 5:54 PM ++
import ast
import json
from django.db import models
from django.utils import six
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey as DFK
from django.db.models.fields.related import ManyToManyField as DM2M
from django.contrib.contenttypes.fields import GenericRelation as CTGenericRelation
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.postgres.fields import JSONField as ps_JSONField

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class GenericRelation(CTGenericRelation):
    """"""

    def contribute_to_class(self, cls, name, **kwargs):
        """
        :param cls:
        :param name:
        :param kwargs:
        :return:
        """
        import pytest;pytest.set_trace()
        super(GenericRelation, self).contribute_to_class(cls, name, **kwargs)


class ManyToManyField(DM2M):
    """"""
    def contribute_to_class(self, cls, name, **kwargs):
        """
        :return:
        """
        if not cls._meta.abstract:

            related_name = self.remote_field.related_name
            if related_name is not None and '{klass}' in related_name:
                self.remote_field.related_name = related_name.format(klass=cls.__name__)

            related_query_name = self.remote_field.related_query_name
            if related_query_name is not None and '{klass}' in related_query_name:
                self.remote_field.related_query_name = related_query_name.format(klass=cls.__name__)

        return super(ManyToManyField, self).contribute_to_class(cls, name, **kwargs)


class ForeignKey(DFK):
    """ """
    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        :param cls:
        :param name:
        :param virtual_only:
        :return:
        Small Hack!: dynamically and uniquely `related name` generation
        """
        if not cls._meta.abstract:

            related_name = self.remote_field.related_name

            if related_name is not None and '{klass}' in related_name:
                self.remote_field.related_name = related_name.format(klass=cls.__name__)

            related_query_name = self.remote_field.related_query_name
            if related_query_name is not None and '{klass}' in related_query_name:
                self.remote_field.related_query_name = related_query_name.format(klass=cls.__name__)
        return super(ForeignKey, self).contribute_to_class(cls, name, virtual_only)


class JSONField(ps_JSONField):
    """
    """
    def value_to_string(self, obj):
        """
         We need string representation of json object
        :param obj:
        :return:
        """
        value = super(JSONField, self).value_to_string(obj)
        if isinstance(value, (list, tuple, set, dict)):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return value


__all__ = [str(x) for x in ('JSONField', 'GenericRelation', 'ForeignKey', 'ManyToManyField')]
