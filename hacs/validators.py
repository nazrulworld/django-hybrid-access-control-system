# -*- coding: utf-8 -*-
# ++ This file `validators.py` is generated at 6/9/16 8:08 PM ++
from __future__ import unicode_literals
import ast
import json
import importlib
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.module_loading import import_string

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in ("UrlModulesValidator", "HttpHandlerValidator", )]


def _validate_importable(string, silent=True):
    """"""
    try:
        _module = import_string(string)
    except ImportError:
        try:
            _module = importlib.import_module(string)
        except ImportError:
            if silent:
                return False
            else:
                raise
    if silent:
        return True
    else:
        return _module


@deconstructible
class UrlModulesValidator(object):
    """"""
    code = 'invalid'
    message = None

    def __init__(self, message=None, code=None):
        """"""
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        """"""
        if not value:
            return
        if isinstance(value, six.string_types):
            try:
                value = json.loads(value)
            except ValueError:
                try:
                    value = ast.literal_eval(value)
                except ValueError:
                    raise ValidationError(
                        message=_("%(value)s must be string from valid json or python list, dict"),
                        code=self.code,
                        params={'value': value}
                    )
        if not isinstance(value, (tuple, list)):
            raise ValidationError(message=_("%(value)s must be instance python amd json list or tuple obj"),
                                  code=self.code,
                                  params={'value': value})

        for x in value:

            try:
                urlconf = _validate_importable(x['url_module'], False)
            except ImportError:
                raise ValidationError(message=_("Invalid url module `%(value)s`!, not importable."),
                                      code=self.code,
                                      params={'value': x['url_module']})

            if not hasattr(urlconf, 'urlpatterns'):
                raise ValidationError(
                    message=_("url module `%(value)s` must have attribute urlpatterns!"),
                    code=self.code,
                    params={'value': x['url_module']}
                )

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        """"""
        return isinstance(other, UrlModulesValidator) and \
            self.code == other.code and \
            self.message == other.message


@deconstructible
class HttpHandlerValidator(object):
    """"""
    code = 'invalid'
    message = None

    def __init__(self, message=None, code=None):
        """"""
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        """"""
        if not value:
            return
        if isinstance(value, six.string_types):
            try:
                value = json.loads(value)
            except ValueError:
                try:
                    value = ast.literal_eval(value)
                except ValueError:
                    raise ValidationError(
                        message=_("%(value)s must be string from valid json or python dict"),
                        code=self.code,
                        params={'value': value}
                    )
        if not isinstance(value, dict):
            raise ValidationError(message=_("%(value)s must be instance python amd json dict obj"),
                                  code=self.code,
                                  params={'value': value})

        for handler_name, handler in six.iteritems(value):
            if not handler:
                continue

            if not _validate_importable(handler):
                raise ValidationError(
                    message=_("Invalid handler! %(value)s is not importable"),
                    code=self.code,
                    params={'value': handler}
                )

    def __ne__(self, other):
        """"""
        return not (self == other)

    def __eq__(self, other):
        """"""
        return isinstance(other, HttpHandlerValidator) and \
            self.code == other.code and \
            self.message == other.message
