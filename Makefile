.PHONY: install test setup lint


lint:
	flake8 job_parser/ tests/

install:
	pip install --upgrade pip
	pip install -r requirements.txt || true
	pip install -e .
	pip install spacy pytest

test:
	pytest tests/

setup: install
	bash setup.sh
