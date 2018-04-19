.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

#############################
# Open a URL in the browser #
#############################
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

##################################
# Display help for this makefile #
##################################
define PRINT_HELP_PYSCRIPT
import re, sys

print("BigchainDB Driver 0.5 developer toolbox")
print("---------------------------------------")
print("Usage:  make COMMAND")
print("")
print("Commands:")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("    %-16s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

##################
# Basic commands #
##################
DOCKER := docker
DC := docker-compose
BROWSER := python -c "$$BROWSER_PYSCRIPT"
HELP := python -c "$$PRINT_HELP_PYSCRIPT"
ECHO := /usr/bin/env echo
IS_DOCKER_COMPOSE_INSTALLED := $(shell command -v docker-compose 2> /dev/null)

# User-friendly check for sphinx-build
help:
	@$(HELP) < $(MAKEFILE_LIST)

install: clean ## Install the package to the active Python's site-packages
	python setup.py install

start: check-deps ## Run BigchainDB driver from source and daemonize it (stop with `make stop`)
	@$(DC) up -d bigchaindb

stop: check-deps ## Stop BigchainDB driver
	@$(DC) stop

reset: check-deps ## Stop and REMOVE all containers. WARNING: you will LOSE all data stored in BigchainDB server.
	@$(DC) down

test: check-deps ## Run all tests once or specify a file/test with TEST=tests/file.py::Class::test
	@$(DC) run --rm bigchaindb-driver pytest ${TEST} -v

test-watch: check-deps ## Run all, or only one with TEST=tests/file.py::Class::test, tests and wait. Every time you change code, test/s will be run again.
	@$(DC) run --rm bigchaindb-driver pytest ${TEST} -f -v
	@$(DC) run --rm bigchaindb-driver pytest ${TEST} -f -v

docs: ## Generate Sphinx HTML documentation, including API docs
	@$(DC) run --rm --no-deps bdocs make -C docs html
	$(BROWSER) docs/_build/html/index.html

lint: check-deps ## Check style with flake8
	@$(DC) run --rm bigchaindb-driver flake8 bigchaindb_driver tests

cov: check-deps ## Check code coverage and open the result in the browser
	@$(DC) run --rm bigchaindb-driver pytest -v --cov=bigchaindb_driver --cov-report html
	$(BROWSER) htmlcov/index.html

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts
	@$(ECHO) "Cleaning was successful."


release: clean ## Package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## Builds source and wheel package
	python setup.py sdist
	ls -l dist

###############
# Sub targets #
###############

check-deps:
ifndef IS_DOCKER_COMPOSE_INSTALLED
	@$(ECHO) "Error: docker-compose is not installed"
	@$(ECHO)
	@$(ECHO) "You need docker-compose to run this command. Check out the official docs on how to install it in your system:"
	@$(ECHO) "- https://docs.docker.com/compose/install/"
	@$(ECHO)
	@$(DC) # docker-compose is not installed, so we call it to generate an error and exit
endif

clean-build: ## Remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
