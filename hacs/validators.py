# -*- coding: utf-8 -*-
# ++ This file `validators.py` is generated at 6/9/16 8:08 PM ++
from __future__ import unicode_literals
import ast
import json
import importlib
from django.utils import six
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.module_loading import import_string
from django.contrib.contenttypes.models import ContentType

from .defaults import HACS_AUTO_DISCOVER_URL_MODULE

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

__all__ = [str(x) for x in ("UrlModulesValidator", "HttpHandlerValidator", "ContentTypeValidator", )]


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
                except (ValueError, SyntaxError):
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
            url_module = x['url_module']
            if isinstance(url_module, (list, tuple)):
                url_module = url_module[0]

            if url_module in getattr(settings, 'HACS_AUTO_DISCOVER_URL_MODULE', HACS_AUTO_DISCOVER_URL_MODULE):
                continue
            try:
                urlconf = _validate_importable(url_module, False)
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
                except (ValueError, SyntaxError):
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


@deconstructible
class ContentTypeValidator(object):
    """"""
    white_list = (("auth", "user"), ("auth", "group"), )
    black_list = ()
    code = "disallowed"
    message = _("Disallowed content type `%(value)s`")

    def __init__(self, message=None, code=None, white_list=None, black_list=None):
        """
        :param message:
        :param code:
        :param white_list:
        :param black_list:
        """
        if message:
            self.message = message
        if code:
            self.code = code
        if white_list:
            self.white_list = white_list
        if black_list:
            self.black_list = black_list

    def __call__(self, value):
        """"""
        try:
            content_type = ContentType.objects.get(pk=value)
        except ContentType.DoesNotExist as exc:
            raise ValidationError(message=smart_text(exc), code='invalid')

        if self.white_list:
            for ct in self.white_list:
                if isinstance(ct, six.string_types):
                    app_label, model = content_type.app_label, ct
                else:
                    app_label, model = ct
                if content_type.app_label == app_label and content_type.model == model:
                    break
            else:
                # Uninterrupted (without break) Loop continuation, value not be in white lists
                raise ValidationError(message=self.message, code=self.code, params={"value": app_label + ":" + model})

        if self.black_list:
            for ct in self.black_list:
                if isinstance(ct, six.string_types):
                    app_label, model = content_type.app_label, ct
                else:
                    app_label, model = ct

                if content_type.app_label == app_label and content_type.model == model:
                    raise ValidationError(message=self.message, code=self.code,
                                          params={"value": app_label + ":" + model})

    def __ne__(self, other):
        """"""
        return not (self == other)

    def __eq__(self, other):
        """"""
        return isinstance(other, ContentTypeValidator) and \
            self.code == other.code and \
            self.message == other.message and \
            self.black_list == other.black_list and \
            self.white_list == other.white_list
