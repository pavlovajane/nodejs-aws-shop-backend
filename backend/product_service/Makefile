# Makefile
.PHONY: test test-coverage install-dev

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest

test-coverage:
	pytest --cov=src --cov-report=html

.PHONY: clean
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
