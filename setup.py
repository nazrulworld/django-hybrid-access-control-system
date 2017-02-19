# -*- coding: utf-8 -*-
"""Installer for the django-hacs package."""
import os
import sys
from setuptools import setup
PY2 = sys.version_info[0] == 2
PY34 = sys.version_info[0:2] >= (3, 4)
PY35 = sys.version_info[0:2] >= (3, 5)

requirements = [
        'Django>=1.10.3',
        'psycopg2',
        'django-redis'
    ]
test_requirements = ['pytest', 'pytest-django', 'pytest-flake8']
if not PY34:
    # we need backport of pathlib
    requirements.append('pathlib2')
    test_requirements.append('mock')

if not PY35:
    requirements.append('typing')


def get_version():
    """"""
    return __import__('hacs').__version__

long_description = (
    open('README.rst').read() +
    '\n' +
    'Contributors\n' +
    '============\n' +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


setup(
    name='django-hacs',
    version=get_version(),
    description="Hybrid Access Control System for Django",
    long_description=long_description,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='Python Django ACL ACS IAM Security Authentication Authorization',
    author='Md Nazrul Islam',
    author_email='email2nazrul@gmail.com',
    url='https://pypi.python.org/pypi/django-hacs',
    license='GPL version 3',
    packages=get_packages('hacs'),
    package_data=get_package_data('hacs'),
    install_requires=requirements,
    extras_require={
        'test': test_requirements,
        'develop': ['jsmin', 'rcssmin']
    }
)
