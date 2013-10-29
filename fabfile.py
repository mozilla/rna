# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import functools
import os

from fabric.api import local as _local


NAME = os.path.basename(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = 'rna'

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_app.settings'
os.environ['PYTHONPATH'] = os.pathsep.join([ROOT])

_local = functools.partial(_local, capture=False)


def cover():
    """Run the test suite with coverage."""
    _local('coverage erase')
    _local('coverage run `which django-admin.py` test')


def cover_report():
    cover()
    _local('coverage report -m %s/*.py %s/*/*.py' % (
           APP_NAME, APP_NAME))
    _local('coverage html %s/*.py %s/*/*.py' % (
           APP_NAME, APP_NAME))


def manage(*args):
    """Run arbitrary commands similar to manage.py."""
    _local('django-admin.py ' + ' '.join(args))


def migrate(migration=''):
    """Update a testing database with south."""
    _local('django-admin.py migrate %s %s' % (APP_NAME, migration))


def shell():
    """Start a Django shell with the test settings."""
    _local('django-admin.py shell')


def shell_plus():
    """Start a django-extensions shell_plus with the test settings."""
    _local('django-admin.py shell_plus')


def serve():
    """Start the Django dev server."""
    _local('django-admin.py runserver')


def runserver_plus():
    """Start the django-extensions werkzeug dev server."""
    _local('django-admin.py runserver_plus')


def syncdb():
    """Create a database for testing in the shell or server."""
    _local('django-admin.py syncdb --noinput')


def schema(initial=False):
    """Create a schema migration for any changes."""
    if initial:
        _local('django-admin.py schemamigration %s --initial' % APP_NAME)
    else:
        _local('django-admin.py schemamigration %s --auto' % APP_NAME)


def test(test_case=''):
    """Run the test suite."""
    _local('django-admin.py test %s' % test_case)


def test_ipdb(test_case=''):
    """Run the test suite using ipdb to debug errors and failures."""
    _local('django-admin.py test %s --ipdb --ipdb-failures' % test_case)
