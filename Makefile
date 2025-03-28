.PHONY: install test setup lint

lint:
	flake8 src/TextExtraction/ tests/

install:
	pip install --upgrade pip
	conda env update --file environment.yml --name base
	pip install spacy pytest

test:
	pytest tests/

setup: install
	bash setup.sh
