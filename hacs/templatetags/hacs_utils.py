# -*- coding: utf-8 -*-
# ++ This file `hacs_utils.py` is generated at 6/4/16 8:44 PM ++
from __future__ import unicode_literals
import ast
import json
from django.utils import six
from django.template import Library
from django.template import TemplateSyntaxError
from django.core.serializers.json import DjangoJSONEncoder

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

register = Library()


@register.filter(is_safe=False)
def to_json(value):
    """
    This method will make JSON like string from any string value that is made from list oo dict object
    :param value:
    :return:
    """
    if not value:
        return ''
    try:
        if isinstance(value, six.string_types):
            value = ast.literal_eval(value)
    except ValueError as exc:
        # before raise error let's check if already json string
        try:
            json.loads(value)
            return value
        except ValueError:
            pass
        raise TemplateSyntaxError("string must be made from dict or list or tuple object. Original message: %s" % exc)
    else:
        return json.dumps(value, cls=DjangoJSONEncoder)


