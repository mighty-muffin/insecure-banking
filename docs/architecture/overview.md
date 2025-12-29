# Architecture Overview

## Project Structure

The project follows Django's standard application structure with clear separation of concerns:

```bash
insecure-banking/
├── db.sqlite3            # SQLite database file
├── Dockerfile            # Docker container definition
├── manage.py             # Django management script
├── mkdocs.yml            # Documentation configuration
├── pyproject.toml        # Project metadata and dependencies
├── requirements.txt      # Production dependencies
├── docs/                 # Documentation
├─ scripts/               # Utility scripts
├── src/                  # Application source code
│   ├── config/           # Django project configuration
│   ├── data/             # Data handling utilities
│   └── web/              # Main web application
└──tests/                 # Test suite
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    ├── security/         # Security tests
    └── e2e/              # End-to-end tests
```

## Application Layers

### Configuration Layer

Located in `src/config/`, this layer contains Django project configuration:

- `settings.py`: Django settings and configuration
- `urls.py`: Root URL routing
- `wsgi.py` and `asgi.py`: WSGI/ASGI application entry points
- `middleware.py`: Custom middleware components

### Data Layer

Located in `src/data/`, this layer handles data operations:

- YAML data processing
- Data serialization and deserialization

### Web Application Layer

Located in `src/web/`, this is the main application layer:

- `models.py`: Database models (User, Account, Operation)
- `views.py`: View functions handling HTTP requests
- `services.py`: Business logic and service functions
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and static assets
- `migrations/`: Database migration files

## Component Interactions

<!-- TODO : Improve this section -->

### URL Routing

URLs are configured in `src/config/urls.py` and mapped to view functions in `src/web/views.py`.

### Views

Views handle HTTP requests, process data through services, and return HTTP responses using templates.

### Services

The service layer in `src/web/services.py` contains business logic separated from view logic, including:

- Authentication operations
- Account operations
- Transaction processing

### Models

Django ORM models represent database tables:

- `User`: User accounts and authentication
- `Account`: Bank accounts with balances
- `Operation`: Transaction records

### Templates

Django templates in `src/web/templates/` provide the user interface:

- Base template with common layout
- Feature-specific templates for different pages
- Partial templates for reusable components

### Static Files

Static assets in `src/web/static/` include:

- Bootstrap CSS framework
- Custom CSS for styling
- JavaScript for interactivity
- Images and fonts

## Database Architecture

The application uses SQLite for simplicity. The schema includes:

- Users table for authentication
- Accounts table for bank accounts
- Operations table for transactions

Foreign key relationships maintain referential integrity between tables.

## Middleware Stack

Custom middleware in `src/config/middleware.py` handles:

- Authentication requirements
- Request/response processing
- Security headers

## Testing Architecture

Tests are organized by type:

- **Unit tests**: Test individual functions and methods in isolation
- **Integration tests**: Test component interactions
- **Security tests**: Test for known vulnerabilities
- **End-to-end tests**: Test complete user workflows using Playwright

## Deployment Architecture

The application can be deployed:

- Locally using Django development server
- In containers using Docker
- Behind a reverse proxy in production environments
