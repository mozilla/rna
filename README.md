RNA
===

Release Notes API

[![Build Status](https://travis-ci.org/mozilla/rna.png)](https://travis-ci.org/mozilla/rna)
[![Coverage Status](https://coveralls.io/repos/mozilla/rna/badge.png)](https://coveralls.io/r/mozilla/rna)

Using the development environment
---------------------------------

Install requirements

    pip install -r requirements/dev.txt

Setup db

    make syncdb_migrate

Start server

    make serve

Using the Python shell

    make shell

Running tests

    make test

Creating South schema migrations

    make schema
    make migrate
