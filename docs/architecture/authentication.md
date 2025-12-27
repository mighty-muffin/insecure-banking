# Authentication and Authorization

## Overview

The application implements a custom authentication system using Django's authentication framework. Authentication is handled through the `AccountService` class and enforced by the `AuthRequiredMiddleware`.

## Authentication Architecture

### Components

1. **AccountService**: Custom authentication backend
2. **AuthRequiredMiddleware**: Enforces authentication
3. **Django User Model**: Standard Django user objects
4. **Session Management**: Django's session framework

### Authentication Flow

```text
User Login Request
       ↓
LoginView.post()
       ↓
authenticate(request)
       ↓
AccountService.authenticate()
       ↓
find_users_by_username_and_password()
  (SQL Injection vulnerable)
       ↓
Create/Retrieve Django User
       ↓
login(request, user)
  (Create session)
       ↓
Redirect to Dashboard
```

## Custom Authentication Backend

### AccountService

Implements Django's `BaseBackend` for custom authentication.

```python
class AccountService(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        username = request.POST.get("username")
        password = request.POST.get("password")
        accounts = self.find_users_by_username_and_password(username, password)
        if len(accounts) == 0:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, password=password)
            user.is_staff = True
            user.is_superuser = username == "john"
            user.save()
        return user
```

### Authentication Process

1. Extract credentials from POST request
2. Query custom Account table (vulnerable to SQL injection)
3. Check if account exists
4. Create or retrieve Django User object
5. Set permissions (is_staff, is_superuser)
6. Return user object or None

### User Creation

Django User objects are created dynamically on first login:

```python
user = User(username=username, password=password)
user.is_staff = True  # All users are staff
user.is_superuser = username == "john"  # Only 'john' is superuser
user.save()
```

### Security Issues

1. **SQL Injection**: Authentication query vulnerable
2. **Plaintext Passwords**: Stored without hashing
3. **Weak Authorization**: Username-based superuser check
4. **No Password Validation**: No complexity requirements
5. **No Account Lockout**: No brute force protection

## Authorization

### Permission Model

The application uses a simple permission model:

- **Authenticated Users**: Can access all banking features
- **Superuser (john)**: No additional privileges implemented
- **Unauthenticated**: Redirected to login

### Access Control

Access control is enforced by `AuthRequiredMiddleware`:

```python
class AuthRequiredMiddleware:
    def __call__(self, request):
        if not request.user.is_authenticated and request.path != "/login":
            return redirect("/login")
        response = self.get_response(request)
        return response
```

### Protected Routes

All routes except `/login` require authentication:

- `/dashboard` - User dashboard
- `/transfer` - Money transfers
- `/activity` - Transaction history
- `/admin` - Admin dashboard (no actual admin check)

### Authorization Vulnerabilities

1. **No Role-Based Access Control (RBAC)**
2. **No Resource-Level Authorization**: Users can access others' data
3. **Admin View Accessible by All**: No superuser check
4. **No Operation-Level Authorization**: No checks for sensitive operations

## Session Management

### Session Creation

Sessions are created on successful login:

```python
from django.contrib.auth import login

def post(self, request, *args, **kwargs):
    user = authenticate(request=request)
    if user is None:
        return HttpResponse(template.render(context, request))
    login(request, user)
    return redirect("/dashboard")
```

### Session Storage

- **Backend**: Database-backed sessions
- **Cookie Name**: `sessionid`
- **Duration**: 2 weeks (default)

### Session Configuration

```python
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True  # JavaScript cannot access
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Session Security Issues

1. **Long Session Lifetime**: 2 weeks
2. **No Session Timeout**: No idle timeout
3. **No Session Regeneration**: Session ID not regenerated on login
4. **HTTP Sessions**: SESSION_COOKIE_SECURE is False
5. **No Concurrent Session Limits**

## User Model

### Custom Account Model

```python
class Account(models.Model):
    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)  # Plaintext
```

### Django User Model

Standard Django User model is used for authentication:

- Created dynamically on first login
- Maps to custom Account model
- Provides Django auth framework integration

### User Attributes

- **username**: Unique identifier
- **password**: Plaintext (security issue)
- **is_staff**: Always True for all users
- **is_superuser**: True only for 'john'

## Login View

### Implementation

```python
class LoginView(TemplateView):
    http_method_names = ["get", "post"]
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        user = authenticate(request=request)
        if user is None:
            template = loader.get_template("login.html")
            context = {"authenticationFailure": True}
            return HttpResponse(template.render(context, request))
        login(request, user)
        return redirect("/dashboard")
```

### Login Process

1. Display login form (GET)
2. User submits credentials (POST)
3. Authenticate user
4. On success: create session and redirect
5. On failure: show error message

### Login Template

The login form is rendered in `login.html`:

- Username field
- Password field
- Submit button
- Error message display

## Logout View

### Implementation

```python
class LogoutView(View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/login")
```

### Logout Process

1. Call `logout(request)`
2. Clear session data
3. Redirect to login page

## Password Management

### Current Implementation

Passwords are stored in plaintext:

```python
class Account(models.Model):
    password = models.CharField(max_length=80)
```

Authentication compares plaintext:

```python
sql = "select * from web_account where username='" + username + "' AND password='" + password + "'"
```

### Issues

1. **Plaintext Storage**: Passwords not hashed
2. **No Strength Requirements**: Any password accepted
3. **No Password Change**: No mechanism to change passwords
4. **No Password Reset**: No forgot password feature
5. **Vulnerable to SQL Injection**: Password field in injectable query

### Correct Implementation

Should use Django's password hashing:

```python
from django.contrib.auth.hashers import make_password, check_password

# Store
hashed = make_password(plain_password)

# Verify
is_valid = check_password(plain_password, hashed_password)
```

## Default Credentials

The application ships with default test credentials:

```text
Username: john
Password: test
```

Additional test users may exist in the database.

## Authentication Testing

Authentication is tested in:

- `tests/integration/test_auth_flow.py`: Authentication flow tests
- `tests/security/test_sql_injection.py`: SQL injection in auth

## Multi-Factor Authentication

Not implemented. Single-factor authentication only.

## OAuth/Social Login

Not implemented. Only local authentication is supported.

## API Authentication

Not applicable. The application is web-only with no API endpoints.

## Authorization Best Practices (Intentionally Violated)

The following best practices are intentionally violated:

1. Plaintext password storage
2. No password hashing
3. SQL injection in authentication
4. No password complexity requirements
5. No account lockout mechanism
6. No rate limiting on login attempts
7. No multi-factor authentication
8. No password expiration
9. Username-based superuser designation
10. No audit logging of authentication events
11. No session regeneration on login
12. Long session lifetimes
13. No resource-level authorization
14. No role-based access control

## Related Documentation

- [Middleware](middleware.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
- [Django Framework](django-framework.md)
- [Services Layer](services.md)
