# Middleware

## Overview

The application uses Django's middleware system to process requests and responses. Middleware components are defined in `src/config/middleware.py` and configured in `src/config/settings.py`.

## Middleware Stack

The middleware stack is defined in `settings.py`:

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

## Django Built-in Middleware

### SecurityMiddleware

Provides security enhancements for Django applications.

**Features:**

- HTTPS redirects (if configured)
- Security headers
- Browser XSS protection

**Configuration:**

Uses default Django settings (intentionally weak for this application).

### SessionMiddleware

Manages user sessions.

**Features:**

- Creates and manages session objects
- Stores session data in database
- Sets session cookies

**Session Backend:**

Database-backed sessions (default).

### CommonMiddleware

Handles common web operations.

**Features:**

- URL normalization
- ETags
- Content-Length headers

**Configuration:**

```python
APPEND_SLASH = False  # Disabled
```

### AuthenticationMiddleware

Adds user authentication to requests.

**Features:**

- Associates users with requests
- Adds `request.user` attribute
- Manages authentication state

**Authentication Backend:**

```python
AUTHENTICATION_BACKENDS = ["web.services.AccountService"]
```

Uses custom authentication backend.

### MessagesMiddleware

Enables Django's messaging framework.

**Features:**

- Flash messages
- One-time notifications
- Cross-request message passing

### XFrameOptionsMiddleware

Protects against clickjacking attacks.

**Features:**

- Sets X-Frame-Options header
- Controls iframe embedding

**Default:**

`DENY` - prevents framing (but may be overridden in views).

## Custom Middleware

### AuthRequiredMiddleware

Custom middleware that enforces authentication on all routes except login.

**Location:** `src/config/middleware.py`

```python
from django.shortcuts import redirect

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path != "/login":
            return redirect("/login")
        response = self.get_response(request)
        return response
```

#### Functionality

1. Checks if user is authenticated
2. If not authenticated and not on login page
3. Redirects to login page
4. Otherwise proceeds with request

#### Excluded Paths

Only `/login` is excluded from authentication check.

#### Security Considerations

- Simple authentication check
- No CSRF validation
- No rate limiting
- No session timeout enforcement

## Middleware Processing Order

### Request Processing

Middleware processes requests in the order defined:

1. SecurityMiddleware
2. SessionMiddleware
3. CommonMiddleware
4. AuthenticationMiddleware
5. MessagesMiddleware
6. XFrameOptionsMiddleware
7. AuthRequiredMiddleware (custom)

### Response Processing

Middleware processes responses in reverse order:

1. AuthRequiredMiddleware
2. XFrameOptionsMiddleware
3. MessagesMiddleware
4. AuthenticationMiddleware
5. CommonMiddleware
6. SessionMiddleware
7. SecurityMiddleware

## Middleware Hooks

### process_request

Called before view is executed. The `AuthRequiredMiddleware` uses the `__call__` method which is equivalent.

### process_response

Called after view is executed. Processes the response before returning to client.

### process_exception

Not implemented in custom middleware.

### process_template_response

Not implemented in custom middleware.

## Session Management

### Session Configuration

Sessions are managed through SessionMiddleware with database backend.

```python
# Default session settings
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = False  # Should be True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Session Storage

Sessions are stored in Django's session table in the database.

### Session Security Issues

- SESSION_COOKIE_SECURE is False (allows HTTP)
- No session timeout enforcement
- No session regeneration on login
- No concurrent session limits

## Authentication Flow

### Login Process

1. User submits credentials to `/login`
2. AuthRequiredMiddleware allows access (login path)
3. AuthenticationMiddleware processes request
4. LoginView.post() calls authenticate()
5. AccountService.authenticate() validates credentials
6. Django User created/retrieved
7. login() creates session
8. Redirect to dashboard

### Request Processing

1. SessionMiddleware loads session data
2. AuthenticationMiddleware loads user from session
3. AuthRequiredMiddleware checks authentication
4. View processes request
5. Response returned

### Logout Process

1. LogoutView.get() called
2. logout() clears session data
3. Redirect to login page

## Security Headers

### Missing Headers

The application is missing important security headers:

```python
# Should be added:
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Current Headers

Only default headers are set by Django middleware.

## Middleware Testing

Middleware behavior is tested in:

- Integration tests that verify authentication flow
- Security tests that check authorization
- Unit tests for middleware components

## Middleware Best Practices (Intentionally Violated)

The following best practices are intentionally violated or not implemented:

1. No rate limiting middleware
2. No request logging middleware
3. No security header enforcement
4. Weak session security
5. No CORS configuration
6. No request size limits
7. No IP filtering
8. No user agent validation
9. Minimal CSRF protection
10. No content security policy

## Custom Middleware Development

### Basic Structure

```python
class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration

    def __call__(self, request):
        # Code executed before view
        
        response = self.get_response(request)
        
        # Code executed after view
        
        return response
```

### Registration

Add to MIDDLEWARE list in settings.py:

```python
MIDDLEWARE = [
    # ... other middleware
    'app.middleware.CustomMiddleware',
]
```

## Middleware Performance

### Performance Considerations

- Middleware executes on every request
- Keep middleware lightweight
- Avoid database queries in middleware
- Cache expensive operations

### Current Performance

The AuthRequiredMiddleware is lightweight:

- Single authentication check
- Database query only if not authenticated
- Minimal processing overhead

## Related Documentation

- [Django Framework](django-framework.md)
- [Authentication and Authorization](authentication.md)
- [Application Architecture](overview.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
