# Project Overview

## Introduction

The Insecure Banking application is a deliberately vulnerable web application built with Django. It simulates a basic online banking system with intentional security flaws designed for security testing, vulnerability assessment training, and educational purposes.

## Purpose

This application serves multiple purposes:

1. Security training and education
2. Vulnerability scanning tool testing
3. Penetration testing practice
4. Security awareness demonstrations
5. CI/CD security testing validation

## Key Features

### Banking Operations

- User authentication and session management
- Account dashboard with balance display
- Cash and credit account management
- Money transfer functionality between accounts
- Transaction history and activity tracking
- User profile management with avatar upload
- Certificate download functionality

### Administrative Features

- Admin dashboard for user management
- User account overview
- System-level operations

### Intentional Vulnerabilities

The application includes the following intentional security vulnerabilities:

- SQL Injection vulnerabilities
- Command Injection flaws
- Insecure Deserialization
- Path Traversal issues
- Weak cryptography implementation
- Cross-Site Request Forgery (CSRF) potential
- Insecure Direct Object References
- Missing authentication checks
- Weak password storage

## Technology Stack

### Backend

- **Framework**: Django 4.2.4
- **Language**: Python 3.10
- **Database**: SQLite
- **WSGI Server**: Built-in Django development server

### Dependencies

- **asgiref**: ASGI utilities for Django
- **sqlparse**: SQL parsing library
- **pycryptodome**: Cryptographic library (used for weak crypto examples)
- **typing-extensions**: Type hint extensions

### Development Tools

- **uv**: Modern Python package manager
- **pytest**: Testing framework
- **pytest-django**: Django integration for pytest
- **pytest-cov**: Code coverage reporting
- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hooks framework

### Infrastructure

- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation

## Project Structure

```text
insecure-banking/
├── src/                    # Application source code
│   ├── config/            # Django project configuration
│   ├── web/               # Main web application
│   └── manage.py          # Django management script
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── security/         # Security-focused tests
├── docs/                  # Documentation
├── .github/              # GitHub Actions workflows
├── Dockerfile            # Container definition
├── pyproject.toml        # Project metadata and configuration
├── requirements.txt      # Python dependencies
└── uv.lock              # Locked dependency versions

```

## Default Credentials

The application comes with pre-configured test users:

- **Username**: john
- **Password**: test

Additional test users may be available in the database initialization.

## Security Notice

This application contains intentional security vulnerabilities and should:

- Never be deployed to production
- Never be exposed to the public internet
- Never handle real user data
- Only be used in isolated testing environments
- Be treated as a security training tool

## License and Usage

This project is designed for educational and testing purposes. Users should be aware that the application is intentionally insecure and should be handled accordingly.
