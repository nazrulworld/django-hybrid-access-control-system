# -*- coding: utf-8 -*-
# ++ This file `lru_wrapped.py` is generated at 4/4/16 4:53 PM ++
from __future__ import unicode_literals
from django.utils import lru_cache

from .utils import get_user_key as utils_get_user_key
from .utils import get_group_key as utils_get_group_key
from .utils import get_site_urlconf as utils_get_site_urlconf
from .utils import get_site_settings as utils_get_site_settings
from .utils import get_site_http_methods as utils_get_site_http_methods
from .utils import site_in_maintenance_mode as utils_site_in_maintenance_mode
from .utils import get_generated_urlconf_file as utils_get_generated_urlconf_file
from .utils import get_installed_apps_urlconf as utils_get_installed_apps_urlconf
from .utils import get_generated_urlconf_module as utils_get_generated_urlconf_module
from .utils import get_site_blacklisted_uri as utils_get_site_blacklisted_uri
from .utils import get_site_whitelisted_uri as utils_get_site_whitelisted_uri


__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

""" All lru cached functions will put here, the purpose is here, we will have non-cached version as well"""


@lru_cache.lru_cache(maxsize=None)
def get_site_settings(site):
    """"""
    return utils_get_site_settings(site)


@lru_cache.lru_cache(maxsize=None)
def get_site_urlconf(site):
    return utils_get_site_urlconf(site)


@lru_cache.lru_cache(maxsize=None)
def site_in_maintenance_mode(site):
    return utils_site_in_maintenance_mode(site)


@lru_cache.lru_cache(maxsize=None)
def get_site_http_methods(site):
    return utils_get_site_http_methods(site)


@lru_cache.lru_cache(maxsize=None)
def get_user_key(request, prefix='hacl', suffix=None):
    return utils_get_user_key(request, prefix, suffix)


@lru_cache.lru_cache(maxsize=None)
def get_site_blacklisted_uri(site):
    return utils_get_site_blacklisted_uri(site)


@lru_cache.lru_cache(maxsize=None)
def get_site_whitelisted_uri(site):
    return utils_get_site_whitelisted_uri(site)


@lru_cache.lru_cache(maxsize=None)
def get_group_key(request, group, prefix='hacl', suffix=None):
    return utils_get_group_key(request, group, prefix, suffix)


@lru_cache.lru_cache(maxsize=None)
def get_generated_urlconf_file(route_name, prefix=None):
    return utils_get_generated_urlconf_file(route_name, prefix)


@lru_cache.lru_cache(maxsize=None)
def get_generated_urlconf_module(filename, validation=True):
    return utils_get_generated_urlconf_module(filename, validation)


@lru_cache.lru_cache(maxsize=None)
def get_installed_apps_urlconf(pattern=r'*urls.py', to_json=False, exclude=()):
    return utils_get_installed_apps_urlconf(pattern, to_json, exclude)


def clean_all_lru_caches():
    """
    :return:
    """
    get_site_settings.cache_clear()
    get_site_urlconf.cache_clear()
    site_in_maintenance_mode.cache_clear()
    get_site_http_methods.cache_clear()
    get_group_key.cache_clear()
    get_user_key.cache_clear()
    get_generated_urlconf_module.cache_clear()
    get_generated_urlconf_file.cache_clear()
    get_installed_apps_urlconf.cache_clear()
    get_site_blacklisted_uri.cache_clear()
    get_site_whitelisted_uri.cache_clear()
