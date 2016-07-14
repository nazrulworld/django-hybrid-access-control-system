HACS(Hybrid Access Control System)
==================================
.. image:: https://badge.fury.io/py/django-hacs.svg
    :target: https://pypi.python.org/pypi/django-hacs/
.. image:: https://travis-ci.org/nazrulworld/django-hybrid-access-control-system.svg?branch=master
    :target: https://travis-ci.org/nazrulworld/django-hybrid-access-control-system
.. image:: https://coveralls.io/repos/github/nazrulworld/django-hybrid-access-control-system/badge.svg?branch=master
    :target: https://coveralls.io/github/nazrulworld/django-hybrid-access-control-system?branch=master

The full featured advanced ``Access Control System`` powered by `Django <https://www.djangoproject.com/>`_. `HACS` provides enterprise standard authorization system,
it also covers IAM(Identity and Access Management).

Features
--------
1. **Django MultiSite:** Support to run `multiple sites <https://docs.djangoproject.com/en/1.9/ref/contrib/sites/#associating-content-with-multiple-sites>`_ with single config file(settings), this is dynamic process, so you can add unlimited sites.

2. **Firewall/Access Control:** Complete  firewall features for your application, almost similar fashion of `IP Table <https://en.wikipedia.org/wiki/Iptables>`_
    a. Custom URL schema: applicable applicable on site, user & group's rules.
    b. HTTP Methods filter: applicable on site, user & group's rules.
    c. Maintenance Mode: applicable on only site's rules.
    d. Regex patterned URL blacklist: applicable on site, user & group's rules.
    e. Regex patterned URL whitelist: applicable on site, user & group's rules.

3. **Advanced Authorization: (coming)** Committed to be more than combination of `Django Guardian <http://django-guardian.readthedocs.io/>`_ and `Django Authority <http://django-authority.readthedocs.io/en/latest/>`_ but definitely base idea could be from those.

4. **Audit Trial: (coming)** This is the part of IAM (Identity and Access Management)

Installation
------------

Install ``django-hacs``, simply use `pip` or `easy_install` ::

     ~$ pip install django-hacs
     or
     ~$ easy_install django-hacs

Install most recent (dev) version of ``django-hacs`` ::

     ~$ git clone https://github.com/nazrulworld/django-hybrid-access-control-system.git django-hacs
     ~$ cd django-hacs
     ~$ python setup.py install

Configuration
-------------
Add ``django-hacs`` at INSTALLED_APPS ::

    INSTALLED_APPS = (
        .................,
        'django.contrib.contentypes',
        'django.contrib.sites',
        'hacs'
    )

Add middleware classes from ``django-hacs`` and also make sure `django.contrib.sites.middleware.CurrentSiteMiddleware`
is added::

    MIDDLEWARE_CLASSES = [
        ............................
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
        'hacs.middleware.DynamicRouteMiddleware',
        'hacs.middleware.FirewallMiddleware',
    ]

Optionally define the writable location, where generated urlconf modules will be stored, default location is ``path to hacs/generated`` ::

    HACS_GENERATED_URLCONF_DIR = "your desired directory location"

Initialize ``django-hacs`` environment and this the starting point::

    ~$ python manage.py init_hacs
    >>> provide your information

Dependencies
------------
- Django 1.9.x or higher


Documentation
-------------

Full documentation for end users can be found in the "docs" folder, and is also available online at http://django-hacs.readthedocs.org/


Routing Rules Management
------------------------
We have two ways to do that.
**Django Admin**
1. Make sure ``admin`` app is installed and ``hacs.urls`` is added into ``urlconf``. i.e ``url(r'^hacs/', include(('hacs.urls', 'hacs'), namespace='hacs'))``
2. Go to ``http://{host}/admin/hacs/``. From there you can manage (add, edit, delete). More details could be found at documentation.

**Django Management Tool**
1. Download sample routing file from `https://github.com/nazrulworld/django-hybrid-access-control-system/blob/master/sample/routes-minimal.json <https://raw.githubusercontent.com/nazrulworld/django-hybrid-access-control-system/master/sample/routes-minimal.json>`_
2. Fill with required information. You can just copy/paste and fill as much as you need, just make sure about valid json and all entries are under one list.
3. Save the json file and keep in mind the location
4. Go to terminal and `cd` to `manage.py`::

    ~$ python manage.py import_route -S <path to json file>

Deploy ``django-hacs``
----------------------

1. You can either follow above instruction and create new routing schema.
2. If you have already routing schema at local and that are ready for production.
    1. Export from local ``~$ python manage.py export_route -d <output file name with full path. i.e /tmp/my-routes.json>``
    2. Now import routing schema from production server's terminal ``~$ python manage.py import_route -S <path to json file>``

Contribute
----------

- Issue Tracker: https://github.com/nazrulworld/django-hybrid-access-control-system/issues
- Source Code: https://github.com/nazrulworld/django-hybrid-access-control-system/
- Documentation: http://django-hacs.readthedocs.org/


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: Django HACS<connect2nazrul@gmail.com>
