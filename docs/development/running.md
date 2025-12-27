# Running the Application

## Local Development

### Start Development Server

```bash
python src/manage.py runserver
```

Default: http://localhost:8000

### Custom Port

```bash
python src/manage.py runserver 8080
```

### All Interfaces

```bash
python src/manage.py runserver 0.0.0.0:8000
```

## Docker

### Build Image

```bash
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg REPO_URL=$(git config --get remote.origin.url) \
  --file Dockerfile \
  --tag insecure-bank-py .
```

### Run Container

```bash
docker run -d \
  --publish 8000:8000 \
  --name insecure-bank-py \
  insecure-bank-py
```

### View Logs

```bash
docker logs insecure-bank-py
```

### Stop Container

```bash
docker stop insecure-bank-py
docker rm insecure-bank-py
```

## Default Credentials

```text
Username: john
Password: test
```

## Available Pages

- `/login` - Login page
- `/dashboard` - Main dashboard
- `/transfer` - Money transfer
- `/activity` - Transaction history
- `/admin` - Admin view
- `/dashboard/userDetail` - User profile

## Development Tools

### Django Shell

```bash
python src/manage.py shell
```

### Database Shell

```bash
python src/manage.py dbshell
```

### Create Superuser

```bash
python src/manage.py createsuperuser
```

### Django Admin

Access at: http://localhost:8000/admin/

## Hot Reload

Django development server automatically reloads on code changes.

## Debugging

### Enable Debug Mode

In `src/config/settings.py`:
```python
DEBUG = True
```

### View SQL Queries

```python
from django.db import connection
print(connection.queries)
```

## Related Documentation

- [Development Setup](setup.md)
- [Docker Containerization](docker.md)
- [Testing](../testing/overview.md)
