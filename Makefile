.PHONY: setup build test clean deploy logs stop help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Setup development environment"
	@echo "  make build    - Build Docker container"
	@echo "  make test     - Run tests"
	@echo "  make deploy   - Deploy to local Kubernetes"
	@echo "  make logs     - View container logs"
	@echo "  make stop     - Stop all containers"
	@echo "  make clean    - Clean up build artifacts"

# Setup development environment
setup:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	chmod +x scripts/*.sh

# Build Docker container
build:
	@echo "Building Docker container..."
	docker-compose build

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=error_management --cov-report=term-missing

# Deploy to local Kubernetes
deploy:
	@echo "Deploying to local Kubernetes..."
	./scripts/generate_certs.sh
	./scripts/deploy_local.sh

# View container logs
logs:
	@echo "Viewing container logs..."
	kubectl logs -f deployment/error-management -n cursor-agent

# Stop all containers
stop:
	@echo "Stopping containers..."
	-docker-compose down
	-kubectl delete -f kubernetes/deployment.yaml -n cursor-agent

# Clean up build artifacts
clean:
	@echo "Cleaning up..."
	-rm -rf venv
	-rm -rf .pytest_cache
	-rm -rf .coverage
	-rm -rf __pycache__
	-rm -rf src/error_management/__pycache__
	-rm -rf tests/__pycache__
	-rm -rf build/
	-rm -rf dist/
	-rm -rf *.egg-info
	-rm -rf certs/

# Security checks
security-check:
	@echo "Running security checks..."
	bandit -r src/
	safety check

# Type checking
type-check:
	@echo "Running type checks..."
	mypy src/

# Lint code
lint:
	@echo "Linting code..."
	flake8 src/ tests/
	black --check src/ tests/

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/

# Run all checks
check: security-check type-check lint test

# Build and deploy
full-deploy: check build deploy

# Development server
dev:
	@echo "Starting development server..."
	python -m error_management /path/to/project

# Generate documentation
docs:
	@echo "Generating documentation..."
	pdoc --html --output-dir docs/ src/error_management

# Continuous testing
watch-test:
	@echo "Running continuous testing..."
	ptw tests/

# Container shell
shell:
	@echo "Opening container shell..."
	kubectl exec -it deployment/error-management -n cursor-agent -- /bin/bash

# View metrics
metrics:
	@echo "Opening metrics dashboard..."
	kubectl port-forward svc/monitoring 9090:9090 -n cursor-agent

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

# Create new test project
create-test-project:
	@echo "Creating test project..."
	mkdir -p test_project
	touch test_project/__init__.py
	@echo 'def test_function():' > test_project/test.py
	@echo '    print("Test function")' >> test_project/test.py

# Run integration tests
integration-test:
	@echo "Running integration tests..."
	pytest tests/test_integration.py -v --log-cli-level=INFO

# Run security tests
security-test:
	@echo "Running security tests..."
	pytest tests/ -v -m security

# Run container tests
container-test:
	@echo "Running container tests..."
	pytest tests/ -v -m container

# Run all tests with coverage
test-coverage: test
	@echo "Generating coverage report..."
	coverage html
	@echo "Coverage report available in htmlcov/index.html"
