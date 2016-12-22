# -*- coding: utf-8 -*-
# ++ This file `patches.py` is generated at 12/17/16 5:50 AM ++
from hacs.globals import HACS_CONTENT_TYPE_USER

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


def apply_model_option_monkey_patch():

    # **** Monkey Patch! enable custom HACS options at Meta class
    import django.db.models.options as options_mod
    setattr(options_mod, 'DEFAULT_NAMES', options_mod.DEFAULT_NAMES + (
        'globally_allowed', 'allowed_content_types', 'hacs_default_permissions'))


def apply_anonymous_user_monkey_patch():
    """
    :return:
    """
    from django.contrib.auth.models import AnonymousUser
    AnonymousUser.__hacs_base_content_type__ = HACS_CONTENT_TYPE_USER

__all__ = [lambda x: str(x), ("apply_model_option_monkey_patch", "apply_anonymous_user_monkey_patch",)]
