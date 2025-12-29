"""Load initial data."""

import os

from django.db import connection, migrations, transaction


class Migration(migrations.Migration):
    """Load initial data from SQL file."""

    dependencies = [
        ("accounts", "0001_initial"),
        ("banking", "0001_initial"),
        ("transfers", "0001_initial"),
    ]

    @transaction.atomic
    def import_data(apps, schema_editor):
        """Import data from SQL file."""
        with open(os.path.join(os.path.dirname(__file__), "data.sql")) as f:
            data = f.read()
            with connection.cursor() as cursor:
                for sql in filter(
                    lambda text: len(text) > 0,
                    map(lambda text: text.strip(), data.split(";")),
                ):
                    cursor.execute(sql)

    operations = [
        migrations.RunPython(import_data),
    ]
