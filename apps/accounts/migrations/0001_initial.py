"""Initial migration for accounts app."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for accounts app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "username",
                    models.CharField(max_length=80, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=80)),
                ("surname", models.CharField(max_length=80)),
                ("password", models.CharField(max_length=80)),
            ],
            options={
                "db_table": "web_account",
                "verbose_name": "Account",
                "verbose_name_plural": "Accounts",
            },
        ),
    ]
