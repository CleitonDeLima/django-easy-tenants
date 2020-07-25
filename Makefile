test:
	pytest -s -vv --no-migrations --cov=easy_tenants --cov-report=xml --cov-report=term-missing
