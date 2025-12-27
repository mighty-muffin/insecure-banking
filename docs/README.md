# Insecure Banking Documentation

## Overview

This documentation provides comprehensive information about the Insecure Banking application, a deliberately vulnerable Django-based web application designed for security testing and educational purposes.

## Table of Contents

### Getting Started

- [Project Overview](project-overview.md)
- [Development Setup](development/setup.md)
- [Running the Application](development/running.md)

### Architecture

- [Application Architecture](architecture/overview.md)
- [Django Framework](architecture/django-framework.md)
- [Database Schema](architecture/database-schema.md)
- [Models](architecture/models.md)
- [Views and URL Routing](architecture/views-urls.md)
- [Services Layer](architecture/services.md)
- [Middleware](architecture/middleware.md)

### Security

- [Security Vulnerabilities](architecture/security-vulnerabilities.md)
- [Authentication and Authorization](architecture/authentication.md)

### Testing

- [Testing Overview](testing/overview.md)
- [Test Structure](testing/structure.md)
- [Unit Tests](testing/unit-tests.md)
- [Integration Tests](testing/integration-tests.md)
- [Security Tests](testing/security-tests.md)
- [Test Configuration](testing/configuration.md)

### CI/CD

- [CI/CD Overview](cicd/overview.md)
- [Main Branch Workflow](cicd/main-workflow.md)
- [Pull Request Workflow](cicd/pr-workflow.md)
- [Tag Workflow](cicd/tag-workflow.md)
- [Pre-commit Hooks](cicd/pre-commit.md)

### Development

- [Dependency Management](development/dependencies.md)
- [Docker Containerization](development/docker.md)
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
