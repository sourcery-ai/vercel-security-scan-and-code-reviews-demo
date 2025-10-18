.PHONY: help install test lint format run docker-build docker-up clean

help:
	@echo "BlogHub - Make commands"
	@echo ""
	@echo "install       Install dependencies"
	@echo "test          Run tests"
	@echo "lint          Run linters"
	@echo "format        Format code"
	@echo "run           Run development server"
	@echo "docker-build  Build Docker image"
	@echo "docker-up     Start Docker containers"
	@echo "clean         Clean up temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/ tests/
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/

run:
	python app.py

docker-build:
	docker build -t bloghub:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	sqlite3 bloghub.db < migrations/001_initial_schema.sql

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -f .coverage
