.PHONY: install test setup lint

lint:
	flake8 job_parser/ tests/

install:
	pip install --upgrade pip
	conda env update --file environment.yml --name base
	pip install spacy pytest

test:
	pytest tests/

setup: install
	bash setup.sh
