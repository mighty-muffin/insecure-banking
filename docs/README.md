# Insecure Banking Documentation

## Overview

This documentation provides comprehensive information about the Insecure Banking application, a deliberately vulnerable Django-based web application designed for security testing and educational purposes.

## Quick Start

New to the project? Start here:

1. [Project Overview](project-overview.md) - Understand what this project is about
2. [Development Setup](development/setup.md) - Set up your local environment
3. [Running the Application](development/running.md) - Start the application
4. [Contributing Guide](development/contributing.md) - Learn how to contribute

## Documentation Sections

### Getting Started

- [Project Overview](project-overview.md)
- [Development Setup](development/setup.md)
- [Running the Application](development/running.md)
- [Docker Deployment](development/docker.md)

### Development

- [Contributing Guide](development/contributing.md)
- [Dependency Management](development/dependencies.md)
- [Code Quality](development/code-quality.md)

### Architecture

- [Application Architecture](architecture/overview.md)

### Testing

- [Testing Overview](testing/overview.md)

## Technology Stack

- **Framework**: Django 4.2.4
- **Language**: Python 3.10+
- **Database**: SQLite3
- **Testing**: pytest, Playwright
- **Code Quality**: Ruff, Bandit, Pre-commit

## Important Notice

This application contains intentional security vulnerabilities and should never be deployed to production or exposed to the internet. It is designed exclusively for controlled testing and educational purposes.

- [Code Quality Tools](development/code-quality.md)
- [Contributing Guidelines](development/contributing.md)

## Quick Reference

### Key Technologies

- Python 3.10
- Django 4.2.4
- SQLite Database
- uv (Package Manager)
- Docker
- GitHub Actions

### Important Commands

```bash
# Install dependencies
uv sync --all-extras --dev --frozen

# Run tests
uv run pytest

# Run application locally
python src/manage.py migrate
python src/manage.py runserver

# Run with Docker
docker build -t insecure-bank-py .
docker run -d -p 8000:8000 insecure-bank-py
```

## Purpose

This application is intentionally designed with security vulnerabilities for educational and testing purposes. It should never be deployed in a production environment or used with real user data.
