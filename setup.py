#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

setup(
    name='django-mozilla-rna',
    version='2.1.2',
    description='Django app for managing Mozilla product release notes.',
    author='Josh Mize',
    author_email='jmize@mozilla.com',
    url='https://github.com/mozilla/rna/',
    license='MPL 2.0',
    packages=['rna', 'rna.management', 'rna.management.commands'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.8,<1.9',
        'djangorestframework>=3.3.0',
        'django-extensions>=1.2.0',
        'django-synctool',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
