RNA
===

Release Notes API

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
