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


def apply_prefetch_one_level_monkey_patch():
    """
    :return: void
    Purpose: we need HacsQueryset::`prefetch_related` lookup unrestricted, as by default `prefetch_related` used
    _default_manager (by default security guard is activated)
    @TODO: Not sure we are patching in the right way.
    See More: django.db.models.fields.related_descriptor.ManyToManyDescriptor::related_manager_cls.get_prefetch_queryset()
    """
    import django.db.models.query as django_query

    def prefetch_one_level(instances, prefetcher, lookup, level):
        """
        Helper function for prefetch_related_objects

        Runs prefetches on all instances using the prefetcher object,
        assigning results to relevant caches in instance.

        The prefetched objects are returned, along with any additional
        prefetches that must be done due to prefetch_related lookups
        found from default managers.
        """
        # prefetcher must have a method get_prefetch_queryset() which takes a list
        # of instances, and returns a tuple:

        # (queryset of instances of self.model that are related to passed in instances,
        #  callable that gets value to be matched for returned instances,
        #  callable that gets value to be matched for passed in instances,
        #  boolean that is True for singly related objects,
        #  cache name to assign to).

        # The 'values to be matched' must be hashable as they will be used
        # in a dictionary.

        rel_qs, rel_obj_attr, instance_attr, single, cache_name = (
            prefetcher.get_prefetch_queryset(instances, lookup.get_current_queryset(level)))
        # HACS: Actual Patch Here Start
        try:
            if rel_qs._disable_security_guard == False:
                rel_qs = rel_qs.unrestricted()
        except (AttributeError, TypeError):
            pass
        # Patch Done!
        # We have to handle the possibility that the QuerySet we just got back
        # contains some prefetch_related lookups. We don't want to trigger the
        # prefetch_related functionality by evaluating the query. Rather, we need
        # to merge in the prefetch_related lookups.
        # Copy the lookups in case it is a Prefetch object which could be reused
        # later (happens in nested prefetch_related).
        additional_lookups = [
            django_query.copy.copy(additional_lookup) for additional_lookup
            in getattr(rel_qs, '_prefetch_related_lookups', ())
            ]
        if additional_lookups:
            # Don't need to clone because the manager should have given us a fresh
            # instance, so we access an internal instead of using public interface
            # for performance reasons.
            rel_qs._prefetch_related_lookups = ()

        all_related_objects = list(rel_qs)

        rel_obj_cache = {}
        for rel_obj in all_related_objects:
            rel_attr_val = rel_obj_attr(rel_obj)
            rel_obj_cache.setdefault(rel_attr_val, []).append(rel_obj)

        to_attr, as_attr = lookup.get_current_to_attr(level)
        # Make sure `to_attr` does not conflict with a field.
        if as_attr and instances:
            # We assume that objects retrieved are homogeneous (which is the premise
            # of prefetch_related), so what applies to first object applies to all.
            model = instances[0].__class__
            try:
                model._meta.get_field(to_attr)
            except django_query.exceptions.FieldDoesNotExist:
                pass
            else:
                msg = 'to_attr={} conflicts with a field on the {} model.'
                raise ValueError(msg.format(to_attr, model.__name__))

        # Whether or not we're prefetching the last part of the lookup.
        leaf = len(lookup.prefetch_through.split(django_query.LOOKUP_SEP)) - 1 == level

        for obj in instances:
            instance_attr_val = instance_attr(obj)
            vals = rel_obj_cache.get(instance_attr_val, [])

            if single:
                val = vals[0] if vals else None
                to_attr = to_attr if as_attr else cache_name
                setattr(obj, to_attr, val)
            else:
                if as_attr:
                    setattr(obj, to_attr, vals)
                else:
                    manager = getattr(obj, to_attr)
                    if leaf and lookup.queryset is not None:
                        try:
                            apply_rel_filter = manager._apply_rel_filters
                        except AttributeError:
                            django_query.warnings.warn(
                                "The `%s.%s` class must implement a `_apply_rel_filters()` "
                                "method that accepts a `QuerySet` as its single "
                                "argument and returns an appropriately filtered version "
                                "of it." % (manager.__class__.__module__, manager.__class__.__name__),
                                django_query.RemovedInDjango20Warning,
                            )
                            qs = manager.get_queryset()
                        else:
                            qs = apply_rel_filter(lookup.queryset)
                    else:
                        qs = manager.get_queryset()
                    qs._result_cache = vals
                    # We don't want the individual qs doing prefetch_related now,
                    # since we have merged this into the current work.
                    qs._prefetch_done = True
                    obj._prefetched_objects_cache[cache_name] = qs

        return all_related_objects, additional_lookups
    setattr(django_query, 'prefetch_one_level', prefetch_one_level)


def apply_EmptyManager_monkey_patch():
    """ This patch will add extra method `unrestricted` that will enable co-work with HACS smoothly.
        For example AnonymousUser groups query. user.groups.unrestricted()
    """
    import django.db.models.manager as ddm

    def unrestricted(self):
        """"""
        return self.get_queryset()
    setattr(ddm.EmptyManager, 'unrestricted', unrestricted)

# Applied
apply_prefetch_one_level_monkey_patch()
apply_model_option_monkey_patch()
apply_EmptyManager_monkey_patch()

__all__ = [lambda x: str(x), ("apply_model_option_monkey_patch", "apply_anonymous_user_monkey_patch",)]
