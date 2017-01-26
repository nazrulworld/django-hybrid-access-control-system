# -*- coding: utf-8 -*-
# ++ This file `functions.py` is generated at 1/17/17 4:37 PM ++
from django.utils import six
from django.db.models import Func
from django.db.models import Value
from django.db.models import CharField
from django.db.models.functions import Cast
from .fields import JSONField

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class JsonbExtractPath(Func):

    function = 'jsonb_extract_path'
    template = '%(function)s(%(expressions)s)'
    arity = 2

    def __init__(self, expression, path, output_field=None):
        """
        :param expression:
        :param path:
        :param output_field:
        """
        output_field = output_field or JSONField()
        if isinstance(expression, six.string_types):
            expression = Cast(expression, output_field)
        if isinstance(path, six.string_types):
            path = Value(path, output_field=CharField())
        super(JsonbExtractPath, self).__init__(expression, path, output_field=output_field)

    def as_postgresql(self, compiler, connection):
        """
        :param compiler:
        :param connection:
        :return:
        """
        sql, params = self.as_sql(compiler, connection)
        # we force to single quote, not wait for cursor!
        # Will helps to print quoted sql statement
        params[0] = "'%s'"% params[0]
        return sql, params
