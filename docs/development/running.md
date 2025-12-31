---
hide:
  - toc
---
# Running the Application

Start the Django development server:

```bash
uv run python manage.py runserver
run python manage.py runserver 0.0.0.0:8000 # Bind to specific IP:PORT
```

This command start the local dev-server:

- The application will be available at [http://localhost:8000](http://localhost:8000).
- Use the following credentials to log into the application:
  - **Username**: john
  - **Password**: test

## Common Management Commands

```bash
uv run python manage.py migrate             # Apply database migrations
uv run python manage.py makemigrations      # Create new migrations after model changes
uv run python manage.py createsuperuser     # Create an administrative user for Django admin
uv run python manage.py shell               # Access the Django interactive shell
```

### Access Django Admin

The Django admin interface is available at [http://localhost:8000/admin](http://localhost:8000/admin).
