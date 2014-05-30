RNA
===

Release Notes API

[![Build Status](https://travis-ci.org/mozilla/rna.png)](https://travis-ci.org/mozilla/rna)
[![Coverage Status](https://coveralls.io/repos/mozilla/rna/badge.png)](https://coveralls.io/r/mozilla/rna)

Using the development environment
=================================

Install requirements
--------------------

    pip install -r requirements/dev.txt
    npm install -g react-tools

Setup db
--------

    make syncdb_migrate

Start server
------------

    make serve

Using the Python shell
----------------------

    make shell

Running tests
-------------

    make test

Creating South schema migrations
--------------------------------

    make schema
    make migrate

Admin customizations based on React
-----------------------------------

Make changes to file(s) in rna/static/jsx

    cd rna/static
    jsx jsx js

This will output standard js files to rna/static/js -- you can also use
the "-w" jsx option to watch the file for changes and continously rebuild
as you develop.
