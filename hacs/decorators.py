# -*- coding: utf-8 -*-
# ++ This file `decorators.py` is generated at 10/24/16 6:11 PM ++
from functools import wraps
from django.utils.decorators import available_attrs
from hacs.security import SecurityManager

__author__ = 'Md Nazrul Islam<connect2nazrul@gmail.com>'


def permission_required(permissions):
    """
    """
    security_manager = SecurityManager()

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            security_manager.check_view_permission(permissions, view_func, request)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
