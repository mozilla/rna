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

    fab syncdb
    fab migrate

Start server

    fab serve

Using the Python shell

    fab shell

Running tests

    fab test

Creating South schema migrations

    fab schema
    fab migrate
