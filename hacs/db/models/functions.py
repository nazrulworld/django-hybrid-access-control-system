# -*- coding: utf-8 -*-
# ++ This file `functions.py` is generated at 1/17/17 4:37 PM ++
from django.utils import six
from django.db.models import Func
from django.db.models import Value
from django.db.models import CharField
from django.contrib.postgres.fields.jsonb import JSONField

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
        return sql, params


class JsonbToArray(Func):

    function = 'SELECT jsonb_array_elements_text'
    template = 'ARRAY(%(function)s(%(expressions)s))'
    arg_joiner = ' -> '
    expression_separator = '__'

    def __init__(self, expression, output_field=None):
        """
        :param expression:
        :param path:
        :param output_field:
        """
        output_field = output_field or CharField()
        paths = list()
        if isinstance(expression, six.string_types):
            parts = expression.split(self.expression_separator)
            expression = parts[0]
            for path in parts[1:]:
                paths.append(Value(path, output_field=CharField()))

        super(JsonbToArray, self).__init__(expression, *paths, output_field=output_field)

    def as_postgresql(self, compiler, connection):
        """
        :param compiler:
        :param connection:
        :return:
        """
        sql, params = self.as_sql(compiler, connection)
        return sql, params
