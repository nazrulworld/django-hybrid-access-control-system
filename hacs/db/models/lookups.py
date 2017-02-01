# -*- coding: utf-8 -*-
# ++ This file `lookups.py` is generated at 2/1/17 3:56 PM ++
from django.contrib.postgres.lookups import HasAnyKeys as ps_HasAnyKeys
from .functions import JsonbToArray
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class HasAnyKeys(ps_HasAnyKeys):
    """"""
    def get_prep_lookup(self):
        """
        :return:
        """
        if isinstance(self.rhs, JsonbToArray):
            return self.rhs._prepare(self.lhs.output_field)
        return super(HasAnyKeys, self).get_prep_lookup()
