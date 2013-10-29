APP_NAME = RNA
APP_DIR = rna
BASEDIR = $(CURDIR)
NAME = $(shell basename $(BASEDIR))
CMD_NAME = django-admin.py

export DJANGO_SETTINGS_MODULE = test_app.settings
export PYTHONPATH := $(BASEDIR):$(PYTHONPATH)

help:
	@echo 'Run commands for $(APP_NAME)'
	@echo
	@echo 'Usage:'
	@echo '    make cover                 run tests with coverage'
	@echo '    make cover_report          run tests with coverage and generate a report'
	@echo '    make manage                run an arbitrary management command'
	@echo '    make migrate               run migrations'
	@echo '    make shell                 open a django python shell'
	@echo '    make shell_plus            run the shell_plus management command'
	@echo '    make serve                 run the django development server'
	@echo '    make serve_plus            run the runserver_plus management command'
	@echo '    make syncdb                create new database tables from models'
	@echo '    make syncdb_migrate        create new tables and run migrations'
	@echo '    make schema                create a new automatic schema migration'
	@echo '    make schema_initial        create the first migration for the app'
	@echo '    make test                  run tests'
	@echo '    make test_ipdb             run tests with ipdb instrumentation'

cover:
	@coverage erase
	@coverage run `which $(CMD_NAME)` test

cover_report: cover
	@coverage report -m $(APP_DIR)/**.py
	@coverage html $(APP_DIR)/**.py

manage:
	@$(CMD_NAME) $(filter-out $@, $(MAKECMDGOALS))

migrate:
	$(CMD_NAME) migrate $(APP_DIR) $(filter-out $@, $(MAKECMDGOALS))

shell:
	@$(CMD_NAME) shell

shell_plus:
	@$(CMD_NAME) shell_plus

serve:
	@$(CMD_NAME) runserver

serve_plus:
	@$(CMD_NAME) runserver_plus

syncdb:
	@$(CMD_NAME) syncdb --noinput

syncdb_migrate:
	@$(CMD_NAME) syncdb --migrate --noinput

schema:
	@$(CMD_NAME) schemamigration $(APP_DIR) --auto

schema_initial:
	@$(CMD_NAME) schemamigration $(APP_DIR) --initial

test:
	@$(CMD_NAME) test $(filter-out $@, $(MAKECMDGOALS))

test_ipdb:
	@$(CMD_NAME) test $(filter-out $@, $(MAKECMDGOALS)) --ipdb --ipdb-failures


.PHONY: cover cover_report manage migrate shell shell_plus serve serve_plus syncdb syncdb_migrate schema schema_initial test test_ipdb
