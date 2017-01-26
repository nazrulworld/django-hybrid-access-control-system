# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# ++ This file `fields.py` is generated at 3/4/16 5:54 PM ++
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.postgres.fields import JSONField as ps_JSONField

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


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


__all__ = [str(x) for x in ('JSONField', )]
