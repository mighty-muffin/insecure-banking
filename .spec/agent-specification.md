# AI-LLM Agent Interaction Specification

## Document Purpose

This specification document provides comprehensive guidance for AI-LLM agents interacting with the Insecure Banking application. It serves as a reference for understanding the project structure, conventions, and best practices for automated code analysis, modification, and testing.

**Version**: 1.0.0  
**Last Updated**: 2025-12-30  
**Repository**: mighty-muffin/insecure-banking

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Code Conventions](#code-conventions)
5. [Development Workflow](#development-workflow)
6. [Testing Strategy](#testing-strategy)
7. [Security Considerations](#security-considerations)
8. [Build and Deployment](#build-and-deployment)
9. [Common Tasks and Patterns](#common-tasks-and-patterns)
10. [Agent Interaction Guidelines](#agent-interaction-guidelines)
11. [API Reference](#api-reference)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

### Purpose

The Insecure Banking application is a **deliberately vulnerable** Django-based web application designed for:

- Security training and education
- Vulnerability scanning tool testing
- Penetration testing practice
- Security awareness demonstrations
- CI/CD security testing validation

⚠️ **IMPORTANT**: This application contains intentional security vulnerabilities and should NEVER be deployed to production or exposed to the public internet.

### Key Features

- User authentication and session management
- Cash and credit account management
- Money transfer functionality
- Transaction history tracking
- User profile management with avatar upload
- Certificate download functionality
- Admin dashboard for user management

### Intentional Vulnerabilities

The application includes the following deliberate security flaws:

- SQL Injection vulnerabilities
- Command Injection flaws
- Insecure Deserialization (pickle)
- Path Traversal issues
- Weak cryptography (DES)
- Cross-Site Request Forgery (CSRF) potential
- Insecure Direct Object References
- Missing authentication checks
- Weak password storage

---

## Technology Stack

### Core Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| Framework | Django | 4.2.4 |
| Database | SQLite | Built-in |
| Package Manager | uv | 0.9.18+ |
| Container | Docker | Latest |

### Key Dependencies

```toml
django==4.2.4
asgiref==3.7.2
sqlparse==0.4.2
pycryptodome==3.18.0
pyyaml==5.3.1
typing-extensions==4.7.1
```

### Development Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| pytest | Testing framework | `pyproject.toml` |
| ruff | Linting & formatting | `pyproject.toml` |
| bandit | Security analysis | `pyproject.toml` |
| pre-commit | Git hooks | `.pre-commit-config.yaml` |
| mkdocs | Documentation | `mkdocs.yml` |
| Docker | Containerization | `Dockerfile` |

---

## Project Structure

```
insecure-banking/
├── .github/                      # GitHub configuration
│   ├── actions/                  # Custom GitHub Actions
│   ├── instructions/             # Coding guidelines
│   │   ├── python.instructions.md
│   │   ├── docker.instructions.md
│   │   └── gha.instructions.md
│   └── workflows/                # CI/CD workflows
│       ├── main.yml              # Main branch workflow
│       ├── pr.yml                # Pull request workflow
│       └── tag.yml               # Tag workflow
├── .spec/                        # AI-LLM agent specifications
│   └── agent-specification.md    # This document
├── docs/                         # Project documentation
│   ├── architecture/             # Architecture documentation
│   ├── development/              # Development guides
│   ├── testing/                  # Testing guides
│   ├── security/                 # Security documentation
│   └── README.md                 # Documentation index
├── src/                          # Application source code
│   ├── config/                   # Django configuration
│   │   ├── settings.py           # Application settings
│   │   ├── test_settings.py      # Test configuration
│   │   ├── urls.py               # URL routing
│   │   ├── middleware.py         # Custom middleware
│   │   ├── wsgi.py               # WSGI entry point
│   │   └── asgi.py               # ASGI entry point
│   ├── web/                      # Main web application
│   │   ├── models.py             # Database models
│   │   ├── views.py              # View controllers
│   │   ├── services.py           # Business logic services
│   │   ├── context_processors.py # Template context processors
│   │   ├── apps.py               # App configuration
│   │   ├── migrations/           # Database migrations
│   │   ├── static/               # Static files (CSS, JS, images)
│   │   └── templates/            # HTML templates
│   ├── data/                     # Data utilities
│   │   └── yaml.py               # YAML processing (insecure)
│   └── manage.py                 # Django management script
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_context_processors.py
│   ├── integration/              # Integration tests
│   │   ├── test_auth_flow.py
│   │   ├── test_admin_flow.py
│   │   ├── test_transfer_flow.py
│   │   └── test_database_integration.py
│   ├── security/                 # Security tests
│   │   ├── test_sql_injection.py
│   │   ├── test_command_injection.py
│   │   ├── test_deserialization.py
│   │   └── test_crypto_weaknesses.py
│   ├── conftest.py               # Global fixtures
│   ├── base.py                   # Base test classes
│   ├── database.py               # Database utilities
│   └── model_helpers.py          # Test helpers
├── scripts/                      # Utility scripts
├── data/                         # Data files
├── .dockerignore                 # Docker ignore patterns
├── .gitignore                    # Git ignore patterns
├── .pre-commit-config.yaml       # Pre-commit hooks config
├── .python-version               # Python version specification
├── Dockerfile                    # Docker container definition
├── pyproject.toml                # Project metadata and config
├── requirements.txt              # Python dependencies
├── uv.lock                       # Locked dependency versions
├── mkdocs.yml                    # Documentation config
├── CHANGELOG.md                  # Version history
└── README.md                     # Project readme
```

---

## Code Conventions

### Python Code Style

The project follows **PEP 8** style guidelines with modifications specified in `pyproject.toml`.

#### Key Conventions

1. **Type Hints**: Use type hints for all function parameters and return values
   ```python
   def transfer_money(from_account: str, to_account: str, amount: float) -> bool:
       pass
   ```

2. **Docstrings**: Follow PEP 257 conventions
   ```python
   def authenticate(username: str, password: str) -> Optional[Account]:
       """
       Authenticate a user with username and password.

       Parameters:
       username (str): The username of the account.
       password (str): The password to verify.

       Returns:
       Optional[Account]: The authenticated account or None.
       """
       pass
   ```

3. **Naming Conventions**:
   - Classes: `PascalCase` (e.g., `CashAccountService`)
   - Functions/Methods: `snake_case` (e.g., `get_account_balance`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_TRANSFER_AMOUNT`)
   - Private methods: prefix with `_` (e.g., `_validate_amount`)

4. **Line Length**: Maximum 128 characters (configured in ruff)

5. **Imports**: Organized in the following order:
   - Standard library imports
   - Third-party imports
   - Django imports
   - Local application imports

#### Ruff Configuration

```toml
[tool.ruff]
line-length = 128
target-version = "py310"
src = ["src"]
extend-exclude = ["__pycache__", ".venv", "install", "tests", "scripts"]
```

### Django-Specific Conventions

1. **Models**: Define in `src/web/models.py`
   - Use descriptive field names
   - Include `__str__` method for string representation
   - Add docstrings for model classes

2. **Views**: Class-based views preferred
   - Inherit from appropriate Django view classes
   - Keep views thin, delegate logic to services

3. **Services**: Business logic layer in `src/web/services.py`
   - One service class per domain entity
   - Methods should be static or class methods
   - Handle all business logic and data access

4. **URL Patterns**: Define in `src/config/urls.py`
   - Use descriptive URL names
   - Follow RESTful conventions where applicable

### Intentional Anti-Patterns

⚠️ The following patterns are **intentionally insecure** and should be preserved:

1. **Raw SQL Queries**: Direct SQL execution without parameterization
   ```python
   # INTENTIONALLY INSECURE - SQL Injection vulnerability
   query = f"SELECT * FROM web_account WHERE username='{username}'"
   cursor.execute(query)
   ```

2. **Insecure Deserialization**: Using pickle for deserialization
   ```python
   # INTENTIONALLY INSECURE - Arbitrary code execution
   import pickle
   data = pickle.loads(serialized_data)
   ```

3. **Command Injection**: Direct OS command execution
   ```python
   # INTENTIONALLY INSECURE - Command injection
   import os
   os.system(f"command {user_input}")
   ```

4. **Weak Cryptography**: Using DES encryption
   ```python
   # INTENTIONALLY INSECURE - Weak encryption
   from Crypto.Cipher import DES
   ```

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone https://github.com/mighty-muffin/insecure-banking.git
cd insecure-banking

# Create virtual environment
uv venv .venv --python 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync --all-extras --dev --frozen

# Run database migrations
python src/manage.py migrate

# Start development server
python src/manage.py runserver
```

### Running the Application

**Local Development**:
```bash
python src/manage.py runserver
# Access at http://localhost:8000
```

**Docker**:
```bash
# Build image
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg REPO_URL=$(git config --get remote.origin.url) \
  --file Dockerfile --tag insecure-bank-py .

# Run container
docker run --detach --publish 8000:8000 --name insecure-bank-py insecure-bank-py
```

### Default Credentials

```
Username: john
Password: test
```

### Pre-commit Hooks

Pre-commit hooks automatically run on git commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Hooks include:
- Trailing whitespace removal
- YAML syntax checking
- File size validation
- Python syntax checking
- Ruff linting and formatting

---

## Testing Strategy

### Test Organization

Tests are organized into three categories:

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test component interactions
3. **Security Tests** (`tests/security/`): Validate intentional vulnerabilities

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test category
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m security       # Security tests only

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::test_account_creation

# Run with coverage
pytest --cov=src

# Run in parallel
pytest -n auto

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Markers

```python
@pytest.mark.unit
def test_model_creation():
    """Test model creation logic."""
    pass

@pytest.mark.integration
def test_user_login():
    """Test complete login flow."""
    pass

@pytest.mark.security
def test_sql_injection():
    """Verify SQL injection vulnerability exists."""
    pass
```

### Coverage Requirements

- Minimum coverage: **92%**
- Coverage reports generated in `tests/coverage/`
- HTML report: `tests/coverage/html/index.html`
- XML report: `tests/coverage/coverage.xml`

### Test Configuration

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.test_settings"
python_paths = ["src"]
testpaths = ["tests"]
pythonpath = "src"
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:tests/coverage/html",
    "--cov-report=xml:tests/coverage/coverage.xml",
    "--cov-fail-under=92",
    "--numprocesses", "auto",
    "--strict-markers",
    "--tb=short",
    "--verbose",
]
```

### Fixtures

Global fixtures are defined in `tests/conftest.py`:

- `db`: Database access
- `client`: Django test client
- `test_user`: Create test user
- `test_account`: Create test account
- `test_cash_account`: Create test cash account
- `test_credit_account`: Create test credit account

---

## Security Considerations

### Security Testing Philosophy

This application's security tests serve a unique purpose:

1. **Validate Vulnerabilities Exist**: Tests should confirm that security vulnerabilities are present and exploitable
2. **Educational Purpose**: Tests demonstrate how vulnerabilities can be exploited
3. **Prevent Fixes**: Tests should fail if vulnerabilities are accidentally fixed

### Security Test Examples

```python
@pytest.mark.security
def test_sql_injection_in_login():
    """Verify SQL injection vulnerability in login."""
    # This test should PASS, confirming the vulnerability exists
    malicious_input = "admin' OR '1'='1"
    result = AccountService.authenticate(malicious_input, "anything")
    assert result is not None  # Vulnerability allows bypass
```

### Security Scanning Tools

**Bandit Configuration** (Security linting):

```toml
[tool.bandit]
severity = "HIGH"
confidence = "HIGH"
exclude-dirs = ["__pycache__", ".venv", "build", "install", "scripts", "tests"]
```

Run Bandit:
```bash
bandit -r src/
```

### Security Documentation

Detailed security documentation is available in:
- `docs/security/` - Security-related documentation
- `docs/architecture/security-vulnerabilities.md` - Vulnerability details

---

## Build and Deployment

### CI/CD Workflows

The project uses GitHub Actions for CI/CD with three main workflows:

#### 1. Pull Request Workflow (`.github/workflows/pr.yml`)

Triggered on: Pull requests to main branch

Steps:
1. Python environment setup
2. Dependency installation
3. Linting with Ruff
4. Security scanning with Bandit
5. Unit test execution
6. Code coverage reporting
7. Docker image build validation

#### 2. Main Branch Workflow (`.github/workflows/main.yml`)

Triggered on: Push to main branch

Steps:
1. All PR workflow steps
2. Docker image build and tag
3. Image push to registry (if configured)
4. Documentation deployment

#### 3. Tag Workflow (`.github/workflows/tag.yml`)

Triggered on: Tag creation (v*.*.*)

Steps:
1. Release build
2. Docker image tagging with version
3. Release artifact creation

### Docker Build

Multi-stage Docker build process:

```dockerfile
# Stage 1: Builder
FROM python:3.10-alpine AS builder
# Install build dependencies
# Install Python packages

# Stage 2: Runtime
FROM python:3.10-alpine
# Copy only runtime dependencies
# Set up non-root user
# Configure application
```

Build command:
```bash
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg REPO_URL=$(git config --get remote.origin.url) \
  --file Dockerfile \
  --tag insecure-bank-py .
```

### Dependency Management

Dependencies are managed with `uv`:

```bash
# Install dependencies
uv sync --all-extras --dev --frozen

# Add new dependency
uv add package-name

# Update dependencies
uv lock

# Export requirements
uv pip compile pyproject.toml -o requirements.txt
```

---

## Common Tasks and Patterns

### Adding a New Model

1. Define model in `src/web/models.py`:
   ```python
   class NewModel(models.Model):
       """Description of the model."""
       field_name = models.CharField(max_length=100)
       
       def __str__(self):
           return self.field_name
   ```

2. Create migration:
   ```bash
   python src/manage.py makemigrations
   ```

3. Apply migration:
   ```bash
   python src/manage.py migrate
   ```

4. Add tests in `tests/unit/test_models.py`

### Adding a New View

1. Define view in `src/web/views.py`:
   ```python
   class NewView(TemplateView):
       """View description."""
       template_name = "template_name.html"
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           # Add context data
           return context
   ```

2. Add URL pattern in `src/config/urls.py`:
   ```python
   path("route/", NewView.as_view(), name="route_name"),
   ```

3. Create template in `src/web/templates/template_name.html`

4. Add integration tests in `tests/integration/`

### Adding a New Service Method

1. Add method to appropriate service class in `src/web/services.py`:
   ```python
   class ExistingService:
       @staticmethod
       def new_method(param: str) -> ReturnType:
           """Method description."""
           # Implementation
           return result
   ```

2. Add unit tests in `tests/unit/test_services.py`:
   ```python
   @pytest.mark.unit
   def test_new_method():
       """Test the new service method."""
       result = ExistingService.new_method("test")
       assert result == expected
   ```

### Adding Documentation

1. Create markdown file in appropriate `docs/` subdirectory
2. Update `docs/README.md` table of contents
3. If using mkdocs, update `mkdocs.yml` navigation

---

## Agent Interaction Guidelines

### For Code Analysis Agents

1. **Understand Context**: This is an intentionally vulnerable application
2. **Preserve Vulnerabilities**: Do not fix security issues unless explicitly asked
3. **Follow Conventions**: Adhere to established code patterns
4. **Test Changes**: Run appropriate tests after modifications
5. **Document Changes**: Update relevant documentation

### For Code Generation Agents

1. **Consistency**: Match existing code style and patterns
2. **Type Hints**: Include type hints for all functions
3. **Docstrings**: Provide comprehensive docstrings
4. **Tests**: Generate corresponding test cases
5. **Security Context**: Understand when to introduce vulnerabilities vs. secure code

### For Testing Agents

1. **Test Categories**: Place tests in appropriate category (unit/integration/security)
2. **Fixtures**: Use existing fixtures from conftest.py
3. **Markers**: Apply appropriate pytest markers
4. **Coverage**: Ensure new code meets 92% coverage threshold
5. **Security Tests**: Validate vulnerabilities exist (opposite of normal security testing)

### For Documentation Agents

1. **Structure**: Follow existing documentation structure
2. **Clarity**: Write clear, concise documentation
3. **Examples**: Include code examples where appropriate
4. **Links**: Cross-reference related documentation
5. **Updates**: Keep documentation synchronized with code

### For Refactoring Agents

1. **Minimal Changes**: Make smallest possible changes
2. **Backward Compatibility**: Maintain existing interfaces
3. **Test Coverage**: Ensure tests still pass
4. **Vulnerability Preservation**: Do not inadvertently fix security issues
5. **Documentation Updates**: Update affected documentation

---

## API Reference

### Core Services

#### AccountService

Located in `src/web/services.py`

```python
class AccountService:
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Account]:
        """Authenticate user with username and password (SQL Injection vulnerable)."""
        
    @staticmethod
    def get_account_by_username(username: str) -> Optional[Account]:
        """Retrieve account by username."""
        
    @staticmethod
    def create_account(username: str, password: str, name: str, surname: str) -> Account:
        """Create new user account."""
```

#### CashAccountService

```python
class CashAccountService:
    @staticmethod
    def get_cash_account(account_id: int) -> Optional[CashAccount]:
        """Retrieve cash account by account ID."""
        
    @staticmethod
    def get_balance(account_id: int) -> float:
        """Get current balance of cash account."""
        
    @staticmethod
    def update_balance(account_id: int, amount: float) -> bool:
        """Update cash account balance."""
```

#### CreditAccountService

```python
class CreditAccountService:
    @staticmethod
    def get_credit_account(account_id: int) -> Optional[CreditAccount]:
        """Retrieve credit account by account ID."""
        
    @staticmethod
    def get_available_credit(account_id: int) -> float:
        """Calculate available credit."""
        
    @staticmethod
    def update_balance(account_id: int, amount: float) -> bool:
        """Update credit account balance."""
```

#### TransferService

```python
class TransferService:
    @staticmethod
    def create_transfer(from_account: int, to_account: int, amount: float) -> Transfer:
        """Create money transfer between accounts."""
        
    @staticmethod
    def process_transfer(transfer_id: int) -> bool:
        """Process pending transfer."""
        
    @staticmethod
    def get_transfers_for_account(account_id: int) -> List[Transfer]:
        """Get all transfers for an account."""
```

#### ActivityService

```python
class ActivityService:
    @staticmethod
    def get_recent_activity(account_id: int, limit: int = 10) -> List[Transaction]:
        """Get recent transaction activity."""
        
    @staticmethod
    def log_transaction(account_id: int, transaction_type: str, amount: float) -> Transaction:
        """Log a new transaction."""
```

#### StorageService

```python
class StorageService:
    @staticmethod
    def save_file(file_data: bytes, filename: str) -> str:
        """Save file to storage (Path Traversal vulnerable)."""
        
    @staticmethod
    def get_file(filename: str) -> Optional[bytes]:
        """Retrieve file from storage (Path Traversal vulnerable)."""
```

### Models

#### Account Model

```python
class Account(models.Model):
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    password = models.CharField(max_length=100)  # Insecurely stored
    is_admin = models.BooleanField(default=False)
    avatar = models.CharField(max_length=200, null=True, blank=True)
```

#### CashAccount Model

```python
class CashAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### CreditAccount Model

```python
class CreditAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Transfer Model

```python
class Transfer(models.Model):
    from_account = models.ForeignKey(CashAccount, on_delete=models.CASCADE, related_name='transfers_sent')
    to_account = models.ForeignKey(CashAccount, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # pending, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### URL Routing

Main URL patterns in `src/config/urls.py`:

```python
urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("transfer/", TransferView.as_view(), name="transfer"),
    path("transfer/confirm/", TransferConfirmView.as_view(), name="transfer_confirm"),
    path("activity/", ActivityView.as_view(), name="activity"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("admin/", AdminView.as_view(), name="admin"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
```

---

## Troubleshooting

### Common Issues

#### 1. Database Migration Errors

**Symptom**: Migration fails or database schema mismatch

**Solution**:
```bash
# Reset database
rm src/db.sqlite3
python src/manage.py migrate
```

#### 2. Test Failures

**Symptom**: Tests fail unexpectedly

**Solutions**:
```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv

# Run specific failing test
pytest tests/path/to/test.py::test_name -vv
```

#### 3. Import Errors

**Symptom**: ModuleNotFoundError

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
uv sync --all-extras --dev --frozen

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### 4. Docker Build Failures

**Symptom**: Docker build fails

**Solutions**:
```bash
# Clear Docker cache
docker builder prune

# Build without cache
docker build --no-cache -t insecure-bank-py .

# Check Docker logs
docker logs insecure-bank-py
```

#### 5. Coverage Threshold Not Met

**Symptom**: Test coverage below 92%

**Solution**:
```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=html

# Open HTML report
open tests/coverage/html/index.html

# Identify uncovered lines and add tests
```

### Debug Commands

```bash
# Run Django shell
python src/manage.py shell

# Check installed packages
uv pip list

# Verify Python version
python --version

# Check Django configuration
python src/manage.py check

# Run linting
ruff check src/

# Run formatting
ruff format src/

# Run security scan
bandit -r src/

# Show pytest configuration
pytest --version
pytest --co -q  # Show collected tests
```

---

## Version History

### v1.0.0 (2025-12-30)

- Initial specification document
- Complete project structure documentation
- Comprehensive API reference
- Testing and CI/CD guidelines
- Agent interaction guidelines

---

## Related Documentation

- [Project README](../README.md)
- [Documentation Index](../docs/README.md)
- [Architecture Overview](../docs/architecture/overview.md)
- [Development Setup](../docs/development/setup.md)
- [Testing Overview](../docs/testing/overview.md)
- [Python Instructions](../.github/instructions/python.instructions.md)
- [Docker Instructions](../.github/instructions/docker.instructions.md)
- [GitHub Actions Instructions](../.github/instructions/gha.instructions.md)

---

## Contact and Support

For questions or issues related to this specification:

1. Review existing documentation in `docs/`
2. Check GitHub Issues
3. Consult the project README
4. Review GitHub Actions workflows for CI/CD patterns

---

## License

This specification document is part of the Insecure Banking application project and follows the same license terms.

---

**End of Specification Document**
