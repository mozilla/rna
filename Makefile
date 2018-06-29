APP_NAME = RNA
APP_DIR = rna
BASEDIR = $(CURDIR)
NAME = $(shell basename $(BASEDIR))
CMD_NAME = django-admin.py

export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH := $(BASEDIR):$(PYTHONPATH)

help:
	@echo 'Run commands for $(APP_NAME)'
	@echo
	@echo 'Usage:'
	@echo '    make cover                 run tests with coverage'
	@echo '    make cover_report          run tests with coverage and generate a report'
	@echo '    make manage                run an arbitrary management command'
	@echo '    make makemigrations        create migrations'
	@echo '    make migrate               apply migrations - create new tables'
	@echo '    make shell                 open a django python shell'
	@echo '    make shell_plus            run the shell_plus management command'
	@echo '    make serve                 run the django development server'
	@echo '    make serve_plus            run the runserver_plus management command'
	@echo '    make test                  run tests'
	@echo '    make test_ipdb             run tests with ipdb instrumentation'

cover:
	@coverage erase
	@coverage run runtests.py

cover_report: cover
	@coverage report -m $(APP_DIR)/**.py
	@coverage html $(APP_DIR)/**.py

manage:
	@$(CMD_NAME) $(filter-out $@, $(MAKECMDGOALS))

makemigrations:
	@$(CMD_NAME) makemigrations --noinput rna

migrate:
	$(CMD_NAME) migrate $(filter-out $@, $(MAKECMDGOALS))

shell:
	@$(CMD_NAME) shell

shell_plus:
	@$(CMD_NAME) shell_plus

serve:
	@$(CMD_NAME) runserver

serve_plus:
	@$(CMD_NAME) runserver_plus

test:
	@./runtests.py $(filter-out $@, $(MAKECMDGOALS))

test_ipdb:
	@./runtests.py $(filter-out $@, $(MAKECMDGOALS)) --ipdb --ipdb-failures


.PHONY: cover cover_report manage makemigrations migrate shell shell_plus serve serve_plus test test_ipdb
