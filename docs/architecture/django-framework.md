# Django Framework

## Framework Version

The application uses Django 4.2.4, a Long-Term Support (LTS) release of the Django web framework.

## Django Configuration

### Project Settings

The Django project is configured through `src/config/settings.py`:

#### Core Settings

```python
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-...")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
```

#### Installed Applications

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "web",
]
```

#### Middleware Stack

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.AuthRequiredMiddleware",
]
```

### URL Configuration

The root URL configuration is defined in `src/config/urls.py`:

- Maps URL patterns to view classes
- Includes Django admin interface
- Routes all banking operations
- Uses path-based routing

### WSGI/ASGI Configuration

The application provides both WSGI and ASGI entry points:

- **WSGI**: `config.wsgi.application` (synchronous)
- **ASGI**: `config.asgi.application` (asynchronous)

## Django Components Used

### Admin Interface

Django's built-in admin interface is enabled at `/admin/`:

- Provides administrative access to models
- Requires superuser authentication
- Not extensively customized in this application

### Authentication System

The application uses Django's authentication framework:

#### Custom Authentication Backend

```python
AUTHENTICATION_BACKENDS = ["web.services.AccountService"]
```

The `AccountService` class implements a custom authentication backend that:

- Authenticates users against the custom Account model
- Uses raw SQL queries (insecure by design)
- Creates Django User objects dynamically
- Manages superuser status

#### Session Management

Django's session framework manages user sessions:

- Session data stored in database
- Session cookie used for authentication
- Logout clears session data

### Template System

Django's template engine is configured with:

- Template directories in the web application
- Context processors for global template variables
- Template inheritance for consistent layouts

#### Context Processors

```python
"context_processors": [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "web.context_processors.version_info",
]
```

Custom context processor:

- **version_info**: Adds Git commit and repository URL to templates

### Static Files

Static file handling configuration:

```python
STATIC_URL = "static/"
```

Static files are served by Django's development server.

### Forms

The application uses Django's form system minimally:

- **TransferForm**: ModelForm for transfer operations
- Form validation enabled
- CSRF protection intentionally weakened

## Django ORM

### Model Definition

Models are defined using Django's ORM:

```python
class Account(models.Model):
    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)
```

### Migrations

Database migrations are managed by Django:

- Initial migration: `web/migrations/0001_initial.py`
- Migration history tracked in database
- Applied via `python manage.py migrate`

### Query Execution

The application intentionally bypasses Django ORM for most queries:

```python
# Instead of using ORM
Account.objects.filter(username=username)

# Raw SQL is used (vulnerable to SQL injection)
sql = "select * from web_account where username='" + username + "'"
Account.objects.raw(sql)
```

This pattern is used to demonstrate SQL injection vulnerabilities.

## Django Management Commands

The application uses standard Django management commands:

### Database Operations

```bash
# Apply migrations
python src/manage.py migrate

# Create migrations
python src/manage.py makemigrations

# Access database shell
python src/manage.py dbshell
```

### Server Operations

```bash
# Run development server
python src/manage.py runserver

# Run on specific port
python src/manage.py runserver 8000

# Run on all interfaces
python src/manage.py runserver 0.0.0.0:8000
```

### User Management

```bash
# Create superuser
python src/manage.py createsuperuser

# Change user password
python src/manage.py changepassword <username>
```

## Django Settings for Testing

Test-specific settings in `src/config/test_settings.py`:

```python
DJANGO_SETTINGS_MODULE = "config.test_settings"
```

Test settings override:

- Database configuration for test database
- Debug settings
- Test-specific middleware
- Cache configuration

## Django Security Features

The application intentionally disables or weakens several Django security features:

### Disabled Features

1. **CSRF Protection**: Partially implemented but can be bypassed
2. **Password Validation**: Empty validators list
3. **XSS Protection**: Not consistently applied
4. **SQL Injection Protection**: ORM bypassed with raw queries

### Security Settings

```python
# Weak secret key (should be environment-specific)
SECRET_KEY = "django-insecure-..."

# Debug mode enabled (should be False in production)
DEBUG = True

# Wildcard allowed hosts (should be specific)
ALLOWED_HOSTS = ["*"]

# Empty password validators (should have validators)
AUTH_PASSWORD_VALIDATORS = []
```

## Django Best Practices (Violated)

The following Django best practices are intentionally violated for educational purposes:

1. Using raw SQL instead of ORM
2. Storing passwords in plaintext
3. Using weak secret keys
4. Enabling debug mode
5. Using wildcard allowed hosts
6. Missing CSRF tokens
7. Direct file system access
8. Insecure deserialization
9. Command injection vulnerabilities
10. Path traversal issues

## Django Database API

### Raw Query Execution

The application uses Django's raw query API:

```python
Account.objects.raw(sql)  # Returns RawQuerySet
```

### Direct Database Connection

Some operations use direct database connections:

```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(sql)
    row = cursor.fetchone()
```

## Django Utilities Used

### File Storage

While Django provides a storage API, the application uses direct file system operations:

```python
# Direct file operations instead of Django storage
with open(file, "rb") as fh:
    return fh.read()
```

### Date/Time Handling

```python
from datetime import date
transfer.date = date.today()
```

## Related Documentation

- [Application Architecture](overview.md)
- [Models](models.md)
- [Views and URL Routing](views-urls.md)
- [Database Schema](database-schema.md)
- [Middleware](middleware.md)
