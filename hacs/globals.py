# -*- coding: utf-8 -*-
# ++ This file `globals.py` is generated at 3/3/16 6:07 AM ++
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        # Python 3.3 or upper
        from threading import get_ident
    except ImportError:
        # Python before 3.3
        from thread import get_ident

# Proxy Translation: @TODO: could be used django translation
_ = lambda x: x
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

HACS_APP_NAME = 'hacs'
HACS_APP_LABEL = HACS_APP_NAME
HACS_GENERATED_FILENAME_PREFIX = 'hacs__generated_'
HACS_SERIALIZED_ROUTE_DIR_NAME = 'hacs_routes'
HACS_CONTENT_TYPE_UTILS = 'utility'
HACS_CONTENT_TYPE_CONTAINER = 'container'
HACS_CONTENT_TYPE_CONTENT = 'content'
HACS_CONTENT_TYPE_STATIC = 'static'
HACS_CONTENT_TYPE_NAME = 'hacs_contenttype'


HTTP_METHOD_LIST = (
    'GET',
    'POST',
    'PUT',
    'HEAD',
    'PATCH',
    'DELETE',
    'OPTIONS'
)
# Actions Definition
HACS_ACTIONS = {
    'list.traverse': {
      "title": _("List: Traverse"),
      "description": "Special action type, just like `execute` permission on directory on UNIX."
                     "This is very important action for child operation!. If"
                     "any user don't have this action permission, she cant do anything with child object even she "
                     "might have local permission"
    },
    'list.view': {
        'title': _("List: View"),
        'description': "In Django ORM sense `query`."
    },
    'list.update': {
        'title': _("List: Update"),
        'description': "In Django ORM sense `update` from QuerySet"
    },
    'list.delete': {
        'title': _("List: View"),
        'description': "In Django ORM sense `delete` from QuerySet"
    },
    'object.view': {
        'title': _("Individual Object View")
    },
    'object.create': {
        'title': _("Create")
    },
    'object.edit': {
        'title': _("Edit")
    },
    'object.delete': {
        'title': _("Delete"),
    },
    'share': {
        'title': "Share",
        "description": "Share means assigning Local Roles"
    },

}

class Local(object):
    """
    Code collect from: https://github.com/pallets/werkzeug/blob/master/werkzeug/local.py
    Simple modified
    """
    __slots__ = ('__storage__', '__ident_func__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

HACS_LOCAL = Local()
HACS_ACCESS_CONTROL_LOCAL = Local()


class HACSSiteCache(object):
    """ Obviously this class is not tread safe, infact we don't need to be. """

    def __init__(self):

        """
        :return:
        """
        self.__storage__ = dict()

    def get(self, key, default=None):
        """
        :param key:
        :param default:
        :return:
        """
        return self.__storage__.get(key, default)

    def set(self, key, value):
        """
        :param key:
        :param value:
        :return:
        """
        return self.__storage__.update({key: value})

    def clear(self):
        """
        :return:
        """
        # Not sure it's make sense of performance optimized way
        del self.__storage__
        self.__storage__ = dict()

    def __getitem__(self, item):
        """
        :param item:
        :return:
        """
        return self.__storage__[item]

    def __setitem__(self, key, value):
        """
        :param key:
        :param value:
        :return:
        """
        self.__storage__[key] = value

    def __delitem__(self, key):
        """
        :param key:
        :return:
        """
        del self.__storage__[key]

    def __len__(self):
        """
        :return:
        """
        return len(self.__storage__)

    def __repr__(self):
        """
        :return:
        """
        return repr(self.__storage__)

    def __str__(self):
        """
        :return:
        """
        return str(self.__storage__)


HACS_SITE_CACHE = HACSSiteCache()
