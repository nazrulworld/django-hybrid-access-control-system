# -*- coding: utf-8 -*-
# ++ This file `events.py` is generated at 7/11/16 9:39 AM ++
from __future__ import unicode_literals
import logging
from django.conf import settings
from django.dispatch import receiver
from django.core.cache import caches
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.apps import apps as django_apps
from django.contrib.contenttypes.models import ContentType

from .globals import HACS_SITE_CACHE
from .utils import set_site_settings
from .lru_wrapped import get_user_key
from .lru_wrapped import get_group_key
from .lru_wrapped import get_site_urlconf
from .defaults import HACS_CACHE_SETTING_NAME
from .lru_wrapped import get_site_http_methods
from .lru_wrapped import site_in_maintenance_mode
from .lru_wrapped import get_site_blacklisted_uri
from .lru_wrapped import get_site_whitelisted_uri
from .lru_wrapped import get_generated_urlconf_file
from .lru_wrapped import get_generated_urlconf_module
from hacs.models import HacsGroupModel
from hacs.globals import HACS_CONTENT_TYPE_CONTENT
from hacs.globals import HACS_CONTENT_TYPE_CONTAINER
from hacs.db.models.signals import queryset_update

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger("hacs.events")


class DummyRequest(object):
    """"""
    def __init__(self):
        """"""
        self.site = None
###########################
# ******** EVENTS ********
###########################

@receiver(pre_delete, dispatch_uid="hacs.events.pre_delete_hacs_model")
def pre_delete_hacs_model(sender, instance, **kwargs):
    """
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    base_contenttype = getattr(sender, '__hacs_base_content_type__', None)
    if base_contenttype is None:
        return

    if base_contenttype == HACS_CONTENT_TYPE_CONTAINER:
        _pre_delete_hacs_container(sender, instance)


@receiver(post_save, sender='hacs.routingtable', dispatch_uid="hacs.events.post_save_routingtable_model")
def post_save_routingtable_model(sender, **kwargs):
    """"""
    if not kwargs['created']:
        get_generated_urlconf_file.cache_clear()
        get_generated_urlconf_module.cache_clear()


@receiver(post_save, sender='hacs.siteroutingrules', dispatch_uid="hacs.post_save_siteroutingrules_model")
def post_save_siteroutingrules_model(sender, **kwargs):
    """"""
    instance = kwargs['instance']
    if instance.is_active and instance.maintenance_mode:
        set_site_settings(instance.site)
    else:
        try:
            del HACS_SITE_CACHE[instance.site.domain]
        except KeyError:
            pass

    _invalidate_site_lru()


@receiver(post_save, sender='hacs.contenttyperoutingrules', dispatch_uid="hacs.events.post_save_ct_routingrules_model")
def post_save_ct_routingrules_model(sender, **kwargs):
    """"""
    cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
    is_group = (kwargs['instance'].content_type.app_label, kwargs['instance'].content_type.model, ) ==\
               ("hacs", "hacsgroupmodel", )
    request = DummyRequest()
    request.site = kwargs['instance'].site

    if is_group:
        group = HacsGroupModel.objects.get(pk=kwargs['instance'].object_id)
        group_key = get_group_key(request, group)
        # Special Case: We have in cache, so need to be cleaned and recreate if exist or create
        if cache.get(group, None):
            cache.delete(group_key)
        # Invalid All user cache and group cache should be auto updated
        for user in group.hacs_grp_users.all():
            request.user = user
            user_key = get_user_key(request)
            if cache.get(user_key, None):
                # Let's Invalid
                cache.delete(user_key)
    else:
        # So this user contenttype
        from django.contrib.auth import get_user_model
        request.user = get_user_model().objects.get(pk=kwargs['instance'].object_id)
        user_key = get_user_key(request)
        if cache.get(user_key, None):
            # Just invalid user cache
            cache.delete(user_key)
    _invalidate_contenttype_lru()


def post_save_container(sender, **kwargs):
    pass

# ********** END Events ***********

#######################################
# Private/Helper Functions            #
#######################################
def _invalidate_site_lru():
    """"""
    get_site_urlconf.cache_clear()
    site_in_maintenance_mode.cache_clear()
    get_site_http_methods.cache_clear()
    get_site_blacklisted_uri.cache_clear()
    get_site_whitelisted_uri.cache_clear()


def _invalidate_contenttype_lru():
    """"""
    get_group_key.cache_clear()
    get_user_key.cache_clear()
    get_generated_urlconf_module.cache_clear()
    get_generated_urlconf_file.cache_clear()


def _pre_delete_hacs_container(model, instance):
    """
    :param model:
    :param instance:
    :return:
    """
    hacs_models = [m for m in django_apps.get_models() if getattr(m, '__hacs_base_content_type__', None) in
                           (HACS_CONTENT_TYPE_CONTENT, HACS_CONTENT_TYPE_CONTAINER) and m != model]

    if not len(hacs_models):
        # No Models We do nothing
        return
    content_type = ContentType.objects.get_for_model(model)

    for model_cls in hacs_models:
        filters = {
            "container_content_type": content_type,
            "parent_container_id": instance.pk
        }
        # Delete All Child records
        model_cls.objects.filter(**filters).delete()



