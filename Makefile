.PHONY: install test clean build docs

install:
	pip install -e .
	pip install -r requirements.txt

test:
	pytest tests/ --cov=biotica

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +

build: clean
	python -m build

docs:
	mkdocs build

serve-docs:
	mkdocs serve

docker-build:
	docker build -t biotica .

docker-run:
	docker run -v $(PWD)/data:/app/data biotica
