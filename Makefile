.PHONY: install test setup lint

lint:
	flake8 src/TextExtraction/ tests/

install:
	pip install --upgrade pip
	conda env update --file environment.yml --name base
	pip install spacy pytest

PYTHON := $(shell which python)

test:
	$(PYTHON) -m pytest tests/

setup: install
	bash setup.sh
