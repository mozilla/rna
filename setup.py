#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

setup(
    name='rna',
    version='1.0',
    description='',
    author='Josh Mize',
    author_email='jmize@mozilla.com',
    #url='',
    #license='',
    packages=[
        'rna', 'rna.management', 'rna.management.commands'],
    install_requires=[
        'South',
        'Django>=1.4.9',
        'djangorestframework>=2.3.7',
        'django-extensions>=1.2.0'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python'],
)
