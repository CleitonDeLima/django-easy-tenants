test:
	python -m pytest

install:
	poetry install
	pip install -r tests/requirements.txt
