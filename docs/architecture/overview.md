# Application Architecture

## Overview

The Insecure Banking application follows the Django MTV (Model-Template-View) architecture pattern. The application is structured as a monolithic Django project with a single web application that handles all banking operations.

## Architecture Pattern

### Django MTV Pattern

The application implements Django's MTV pattern:

- **Models**: Define the data structure and database schema
- **Templates**: HTML files with Django template language for rendering UI
- **Views**: Handle HTTP requests and return responses

### Layered Architecture

```text
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (Templates, Static Resources)    │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│          Controller Layer           │
│       (Views, URL Routing)          │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Business Logic Layer        │
│            (Services)               │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│           Data Layer                │
│      (Models, Database)             │
└─────────────────────────────────────┘
```

## Project Structure

### Configuration (`src/config/`)

The Django project configuration directory contains:

- **settings.py**: Application settings and configuration
- **urls.py**: Root URL configuration
- **wsgi.py**: WSGI application entry point
- **asgi.py**: ASGI application entry point
- **middleware.py**: Custom middleware components
- **test_settings.py**: Test-specific configuration

### Web Application (`src/web/`)

The main application directory contains:

- **models.py**: Database models
- **views.py**: View classes and functions
- **services.py**: Business logic and data access services
- **context_processors.py**: Template context processors
- **apps.py**: Application configuration
- **migrations/**: Database migration files
- **static/**: Static files (CSS, JavaScript, images)
- **templates/**: HTML templates

## Component Interaction

### Request Flow

1. **HTTP Request** arrives at Django
2. **URL Router** matches the request to a view
3. **Middleware** processes the request
4. **View** handles the request:
   - Authenticates user
   - Calls service layer for business logic
   - Fetches data from models
5. **Template** renders the response
6. **Middleware** processes the response
7. **HTTP Response** is returned to client

### Authentication Flow

```text
User Request
    ↓
AuthRequiredMiddleware (checks if authenticated)
    ↓
AccountService.authenticate()
    ↓
Database Query (SQL Injection vulnerability)
    ↓
Django User Creation/Retrieval
    ↓
Session Management
    ↓
Access Granted/Denied
```

## Core Components

### Models

Define the data structure for:

- User accounts (Account)
- Cash accounts (CashAccount)
- Credit accounts (CreditAccount)
- Transfers (Transfer)
- Transactions (Transaction)

### Views

Implement the following view types:

- **TemplateView**: For pages that render templates
- **View**: For endpoints that handle specific actions
- **Class-based views**: Used throughout for consistency

### Services

Business logic layer including:

- **AccountService**: User authentication and management
- **CashAccountService**: Cash account operations
- **CreditAccountService**: Credit account management
- **ActivityService**: Transaction history
- **TransferService**: Money transfer operations
- **StorageService**: File storage operations

### Middleware

Custom middleware components:

- **AuthRequiredMiddleware**: Enforces authentication on protected routes

## Database Architecture

### Database Engine

- **Type**: SQLite
- **Location**: `src/db.sqlite3`
- **Mode**: File-based, single-file database

### Schema Design

The database uses a simple relational schema with the following tables:

- `web_account`: User account information
- `web_cashaccount`: Cash account details
- `web_creditaccount`: Credit account details
- `web_transfer`: Transfer records
- `web_transaction`: Transaction history

### Data Access Pattern

The application uses raw SQL queries (intentionally insecure) instead of Django ORM for most operations. This design choice enables SQL injection vulnerabilities for testing purposes.

## Configuration Management

### Settings Hierarchy

1. **Base settings** in `settings.py`
2. **Environment variables** override base settings
3. **Test settings** in `test_settings.py` for testing

### Key Configuration

- **SECRET_KEY**: Django secret key (insecurely set by default)
- **DEBUG**: Debug mode (enabled by default)
- **ALLOWED_HOSTS**: Allowed host headers (set to wildcard)
- **DATABASES**: Database configuration
- **INSTALLED_APPS**: Django applications
- **MIDDLEWARE**: Middleware stack

## Static Files

Static files are organized in:

```text
src/web/static/
├── css/          # Stylesheets
├── js/           # JavaScript files
├── images/       # Image files
└── resources/    # Other resources
    └── avatars/  # User avatar storage
```

## Template Organization

Templates are stored in:

```text
src/web/templates/
├── login.html              # Login page
├── dashboard.html          # Main dashboard
├── accountActivity.html    # Transaction history
├── newTransfer.html        # Transfer form
├── transferCheck.html      # Transfer confirmation
├── transferConfirmation.html  # Transfer success
├── userDetail.html         # User profile
├── admin.html              # Admin dashboard
└── creditActivity.html     # Credit account activity
```

## Deployment Architecture

### Development

- Django development server
- SQLite database
- Local file storage

### Docker

- Alpine-based Python container
- Multi-stage build
- Non-root user execution
- Port 8000 exposed

## Security Considerations

The architecture intentionally includes security vulnerabilities:

- Direct SQL query execution without parameterization
- Insecure deserialization with pickle
- Command injection through os.system
- Weak encryption with DES
- Missing CSRF protection
- Path traversal vulnerabilities

These are documented in detail in the [Security Vulnerabilities](security-vulnerabilities.md) documentation.

## Scalability Limitations

The current architecture has intentional limitations:

- Single-threaded development server
- SQLite database (not suitable for concurrent access)
- Local file storage (not distributed)
- No caching layer
- No load balancing

These limitations are acceptable given the application's educational purpose.

## Related Documentation

- [Django Framework](django-framework.md)
- [Database Schema](database-schema.md)
- [Models](models.md)
- [Views and URL Routing](views-urls.md)
- [Services Layer](services.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
