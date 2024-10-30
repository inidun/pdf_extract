SHELL := /bin/bash
SOURCE_FOLDERS=pdf_extract scripts tests
PACKAGE_FOLDER=pdf_extract
BLACK_ARGS=--line-length 120 --target-version py310 --skip-string-normalization -q
MYPY_ARGS=--show-column-numbers --no-error-summary --python-version 3.10
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py 310

black:
	@poetry run black $(BLACK_ARGS) $(SOURCE_FOLDERS)
isort:
	@poetry run isort $(ISORT_ARGS) $(SOURCE_FOLDERS)
tidy: isort black
.PHONY: black isort tidy

pylint:
	@poetry run pylint $(SOURCE_FOLDERS)

.ONESHELL: pylint_diff
pylint_diff:
	@delta_files=$$(git status --porcelain | awk '{print $$2}' | grep -E '\.py$$' | tr '\n' ' ')
	@if [[ "$$delta_files" != "" ]]; then
		poetry run pylint $$delta_files
	fi

notes:
	@poetry run pylint --notes=FIXME,XXX,TODO --disable=all --enable=W0511 -f colorized $(SOURCE_FOLDERS)

mypy:
	@poetry run mypy $(MYPY_ARGS) $(SOURCE_FOLDERS) || true

mypy-strict:
	@poetry run mypy $(MYPY_ARGS) --strict $(SOURCE_FOLDERS) || true

lint: tidy pylint
typing: lint mypy
typing-strict: lint mypy-strict
.PHONY: pylint pylint_diff notes mypy mypy-strict lint typing typing-strict

clean:
	@rm -rf .coverage coverage.xml htmlcov .nox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
.PHONY: clean

test:
	@poetry run pytest --durations=0 tests/
coverage:
	@poetry run pytest --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/
test-no-java:
	@poetry run pytest -m "not java" --durations=0 tests/
test-java:
	# @poetry run pytest -m "java" -p no:faulthandler tests/
	@poetry run pytest -m "java" tests/
retest:
	@poetry run pytest --durations=0 --last-failed tests
.PHONY: test coverage test-no-java test-java retest

.PHONY: help

help:
	@echo "Higher level recepies: "
	@echo " make clean            Removes temporary files, caches, and build files"
	@echo " make lint             Runs tidy and pylint"
	@echo " make typing           Runs tidy, pylint, and mypy"
	@echo " make typing-strict    Runs tidy, pylint, and mypy with strict mode"
	@echo " make test             Runs tests"
	@echo " make coverage         Runs tests with code coverage"
	@echo " make tidy             Runs black and isort"
	@echo "  "
	@echo "Lower level recepies: "
	@echo " make black            Runs black"
	@echo " make isort            Runs isort"
	@echo " make mypy             Runs mypy"
	@echo " make mypy-strict      Runs mypy with strict mode"
	@echo " make notes            Runs pylint with notes"
	@echo " make pylint           Runs pylint"
	@echo " make pylint_diff      Runs pylint on changed files only"
