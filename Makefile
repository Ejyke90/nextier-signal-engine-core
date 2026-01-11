.PHONY: setup dev test build clean

# Development environment setup
setup:
	python -m pip install -e ".[dev]"

# Start development environment
dev:
	docker compose up -d

# Run tests
test:
	pytest

# Build Docker images
build:
	docker compose build

# Clean up
clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
