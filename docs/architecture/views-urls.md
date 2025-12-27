# Views and URL Routing

## Overview

The application uses Django's class-based views for handling HTTP requests. Views are organized in `src/web/views.py` and mapped to URLs through `src/config/urls.py`.

## URL Configuration

### Root URL Patterns

Located in `src/config/urls.py`:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("", views.DashboardView.as_view(), name="home"),
    path("admin", views.AdminView.as_view(), name="admin"),
    path("activity", views.ActivityView.as_view(), name="activity"),
    path("activity/<str:account>/detail", views.ActivityView.as_view(), name="activity"),
    path("activity/detail", views.ActivityView.as_view(), name="activity"),
    path("activity/credit", views.ActivityCreditView.as_view(), name="activityCredit"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/userDetail", views.UserDetailView.as_view(), name="userDetail"),
    path("dashboard/userDetail/creditCardImage", views.CreditCardImageView.as_view(), name="creditCardImage"),
    path("dashboard/userDetail/avatar", views.AvatarView.as_view(), name="avatar"),
    path("dashboard/userDetail/avatar/update", views.AvatarUpdateView.as_view(), name="avatarUpdate"),
    path("dashboard/userDetail/certificate", views.CertificateDownloadView.as_view(), name="certificateDownload"),
    path("dashboard/userDetail/maliciouscertificate", views.MaliciousCertificateDownloadView.as_view(), name="maliciousCertificateDownload"),
    path("dashboard/userDetail/newcertificate", views.NewCertificateView.as_view(), name="newCertificate"),
    path("transfer", views.TransferView.as_view(), name="transfer"),
    path("transfer/confirm", views.TransferView.as_view(), name="transfer"),
]
```

### URL Patterns Structure

- **Root paths**: Direct endpoints (/, /login, /logout)
- **Admin paths**: Administrative functionality (/admin)
- **Dashboard paths**: User dashboard and profile (/dashboard/*)
- **Activity paths**: Transaction history (/activity/*)
- **Transfer paths**: Money transfer operations (/transfer/*)

## View Classes

### LoginView

Handles user authentication.

```python
class LoginView(TemplateView):
    http_method_names = ["get", "post"]
    template_name = "login.html"
```

#### Supported Methods

- **GET**: Display login form
- **POST**: Process login credentials

#### Request Flow

1. User submits username and password
2. `authenticate()` called with request
3. On success: create session and redirect to dashboard
4. On failure: render login page with error message

#### Security Issues

- SQL injection in authentication query
- No rate limiting
- No CSRF protection enforcement

### LogoutView

Handles user logout.

```python
class LogoutView(View):
    http_method_names = ["get"]
```

#### Supported Methods

- **GET**: Logout user and redirect to login

#### Request Flow

1. Call `logout(request)` to clear session
2. Redirect to `/login`

### DashboardView

Main dashboard displaying account overview.

```python
class DashboardView(TemplateView):
    http_method_names = ["get"]
    template_name = "dashboard.html"
```

#### Context Data

- **account**: Current user's account information
- **cashAccounts**: List of user's cash accounts
- **creditAccounts**: List of user's credit accounts

#### Supported Methods

- **GET**: Display dashboard

### AdminView

Administrative dashboard for viewing all users.

```python
class AdminView(TemplateView):
    http_method_names = ["get"]
    template_name = "admin.html"
```

#### Context Data

- **account**: Current admin's account information
- **accounts**: List of all user accounts

#### Supported Methods

- **GET**: Display admin dashboard

#### Security Issues

- No actual admin permission check
- All authenticated users can access
- Exposes all user data

### ActivityView

Displays transaction history for an account.

```python
class ActivityView(TemplateView):
    http_method_names = ["get", "post"]
    template_name = "accountActivity.html"
```

#### Context Data

- **account**: Current user's account
- **cashAccounts**: User's cash accounts
- **firstCashAccountTransfers**: Transaction history
- **actualCashAccountNumber**: Selected account number

#### Supported Methods

- **GET**: Display account activity
- **POST**: Change displayed account

#### Account Selection

Account can be selected via:

1. URL parameter: `/activity/<account>/detail`
2. POST parameter: `number`
3. Default: First cash account

### ActivityCreditView

Displays credit account activity.

```python
class ActivityCreditView(TemplateView):
    http_method_names = ["get"]
    template_name = "creditActivity.html"
```

#### Context Data

- **account**: Current user's account
- **actualCreditCardNumber**: Selected credit card number

#### Supported Methods

- **GET**: Display credit activity (requires `number` parameter)

### UserDetailView

Displays user profile information.

```python
class UserDetailView(TemplateView):
    http_method_names = ["get"]
    template_name = "userDetail.html"
```

#### Context Data

- **account**: User's account information
- **creditAccounts**: User's credit accounts
- **accountMalicious**: Duplicate account reference (for demonstration)

#### Supported Methods

- **GET**: Display user details

### AvatarView

Serves user avatar images.

```python
class AvatarView(View):
    http_method_names = ["get"]
```

#### Supported Methods

- **GET**: Return avatar image (requires `image` parameter)

#### Request Flow

1. Get `image` parameter from query string
2. Check if file exists in avatars directory
3. Return image file or default avatar

#### Security Issues

- Path traversal vulnerability
- No input validation on image parameter
- Direct file system access

### AvatarUpdateView

Handles avatar image uploads.

```python
class AvatarUpdateView(View):
    http_method_names = ["post"]
```

#### Supported Methods

- **POST**: Upload new avatar image

#### Request Flow

1. Receive uploaded file from `imageFile` field
2. Save to avatars directory as `{username}.png`
3. Redirect to user detail page

#### Security Issues

- No file type validation
- No file size limits
- No malware scanning
- Direct file system write

### TransferView

Handles money transfer operations.

```python
class TransferView(TemplateView):
    http_method_names = ["get", "post"]
    template_name = "newTransfer.html"
```

#### Context Data

- **account**: Current user's account
- **cashAccounts**: User's cash accounts
- **transfer**: Transfer form data

#### Supported Methods

- **GET**: Display transfer form
- **POST**: Process transfer or confirmation

#### Request Flow

##### Initial Transfer

1. User fills transfer form
2. POST to `/transfer`
3. For "Personal" account type: show confirmation page
4. For other types: process immediately

##### Transfer Confirmation

1. User confirms on confirmation page
2. POST to `/transfer/confirm` with action="confirm"
3. Retrieve pending transfer from session
4. Process transfer and show confirmation

#### Security Issues

- Command injection in transfer logging
- Session data manipulation possible
- Cookie-based account type selection
- No transaction limits
- Insufficient validation

### CertificateDownloadView

Generates certificate download (safe version).

```python
class CertificateDownloadView(View):
    http_method_names = ["post"]
```

#### Supported Methods

- **POST**: Generate and download certificate

#### Request Flow

1. Create pickled Trusted object
2. Return as downloadable file

### MaliciousCertificateDownloadView

Generates malicious certificate (unsafe version).

```python
class MaliciousCertificateDownloadView(View):
    http_method_names = ["post"]
```

#### Supported Methods

- **POST**: Generate and download malicious certificate

#### Request Flow

1. Create pickled Untrusted object with malicious code
2. Generate checksum
3. Return as downloadable file

#### Security Issues

- Demonstrates insecure deserialization
- Malicious code execution on unpickling

### NewCertificateView

Handles certificate upload and processing.

```python
class NewCertificateView(View):
    http_method_names = ["post"]
```

#### Supported Methods

- **POST**: Upload and process certificate file

#### Request Flow

1. Receive uploaded certificate file
2. Verify checksum matches malicious certificate
3. Unpickle file (executes code)
4. Return success/failure message

#### Security Issues

- Insecure deserialization vulnerability
- Arbitrary code execution
- No file validation

### CreditCardImageView

Serves credit card images.

```python
class CreditCardImageView(View):
    http_method_names = ["get"]
```

#### Supported Methods

- **GET**: Return credit card image file

#### Request Flow

1. Get `url` parameter
2. Extract filename and extension
3. Read file from resources directory
4. Return as downloadable image

#### Security Issues

- Path traversal vulnerability
- No input validation
- Direct file system access
- Information disclosure

## View Helpers

### get_file_checksum

Generates weak DES-based checksum.

```python
def get_file_checksum(data: bytes) -> str:
    (dk, iv) = (secretKey, secretKey)
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    padded = pad(data, DES.block_size)
    encrypted = crypter.encrypt(padded)
    return base64.b64encode(encrypted).decode("UTF-8")
```

#### Security Issues

- Uses weak DES encryption
- Static IV same as key
- Not a proper checksum/hash

### to_traces

Executes system commands (command injection).

```python
def to_traces(string: str) -> str:
    return str(os.system(string))
```

#### Security Issues

- Direct command execution
- No input sanitization
- Command injection vulnerability

## View Base Classes

### TemplateView

Used for views that render templates:

- LoginView
- DashboardView
- AdminView
- ActivityView
- ActivityCreditView
- UserDetailView
- TransferView

### View

Used for action-based views:

- LogoutView
- AvatarView
- AvatarUpdateView
- CertificateDownloadView
- MaliciousCertificateDownloadView
- NewCertificateView
- CreditCardImageView

## HTTP Method Handling

### Allowed Methods

Each view explicitly defines allowed HTTP methods:

```python
http_method_names = ["get", "post"]
```

Requests with other methods (PUT, DELETE, etc.) are rejected with 405 Method Not Allowed.

## Context Processing

### Template Context

Views provide context data through `get_context_data()`:

```python
def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(**kwargs)
    principal = self.request.user
    context["account"] = AccountService.find_users_by_username(principal.username)[0]
    return context
```

### Global Context

Additional context added by context processors:

- `version_info`: Git commit and repository URL

## Response Types

### HTML Responses

Most views return HTML responses:

```python
return HttpResponse(template.render(context, request))
```

### Redirects

Used after POST operations:

```python
return redirect("/dashboard")
```

### File Downloads

Binary file responses:

```python
return HttpResponse(
    certificate,
    content_type="application/octet-stream",
    headers={"Content-Disposition": file_name},
)
```

### Image Responses

Image file responses:

```python
return HttpResponse(data, content_type="image/png")
```

## Session Management

### Session Storage

Transfer confirmation uses session storage:

```python
request.session["pendingTransfer"] = json.dumps(transfer.as_dict())
```

### Session Retrieval

```python
transfer = Transfer()
transfer.from_dict(json.loads(request.session["pendingTransfer"]))
del request.session["pendingTransfer"]
```

## Cookie Usage

Account type stored in cookie:

```python
response.set_cookie("accountType", "Personal")
```

Retrieved in POST handler:

```python
account_type = request.COOKIES.get("accountType")
```

## Form Processing

### Form Validation

Forms are validated but not strictly:

```python
transfer_form = TransferForm(request.POST)
transfer_form.is_valid()  # Called but result not checked
transfer = transfer_form.instance
```

### Form Data Access

Direct POST data access:

```python
username = request.POST.get("username")
password = request.POST.get("password")
```

## Related Documentation

- [URL Routing Reference](https://docs.djangoproject.com/en/4.2/topics/http/urls/)
- [Class-Based Views](https://docs.djangoproject.com/en/4.2/topics/class-based-views/)
- [Services Layer](services.md)
- [Security Vulnerabilities](security-vulnerabilities.md)
- [Models](models.md)
