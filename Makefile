PYTHON ?= python3
MANAGE := $(PYTHON) manage.py

.PHONY: run migrate createsuperuser test

run:
	$(MANAGE) runserver 0.0.0.0:8000

migrate:
	$(MANAGE) migrate

createsuperuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test
