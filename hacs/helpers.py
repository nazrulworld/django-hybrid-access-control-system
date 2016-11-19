# -*- coding: utf-8 -*-
# ++ This file `helpers.py` is generated at 10/26/16 6:25 PM ++
from __future__ import unicode_literals
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


Empty = object()


class LazyUserModelLoad(SimpleLazyObject):
    """
    """
    def __call__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        if self._wrapped is Empty:
            self._setup()
        # AS wrapped is nothing but Class so class could be initialized
        return self._wrapped(*args, **kwargs)


user_model_lazy = LazyUserModelLoad(get_user_model)


__all__ = [str(x) for x in (
    "user_model_lazy",
)]

