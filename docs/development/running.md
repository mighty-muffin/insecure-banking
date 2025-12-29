# Running the Application

## Local Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at [http://localhost:8000](http://localhost:8000).

## Login Credentials

Use the following credentials to log into the application:

- **Username**: john
- **Password**: test

## Common Management Commands

### Database Migrations

Apply database migrations:

```bash
python manage.py migrate
```

Create new migrations after model changes:

```bash
python manage.py makemigrations
```

### Create Superuser

Create an administrative user for Django admin:

```bash
python manage.py createsuperuser
```

### Access Django Admin

The Django admin interface is available at [http://localhost:8000/admin](http://localhost:8000/admin).

### Run Django Shell

Access the Django interactive shell:

```bash
python manage.py shell
```

### Collect Static Files

Collect static files for production deployment:

```bash
python manage.py collectstatic
```

## Development Server Options

### Change Port

Run the server on a different port:

```bash
python manage.py runserver 8080
```

### Bind to All Interfaces

Make the server accessible from other machines on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running to stop it.

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, either:

- Stop the process using port 8000
- Run the server on a different port using `python manage.py runserver 8080`

### Database Locked

If you encounter database locking issues with SQLite, ensure only one server instance is running.

### Static Files Not Loading

Run `python manage.py collectstatic` to collect static files if they are not loading correctly.
