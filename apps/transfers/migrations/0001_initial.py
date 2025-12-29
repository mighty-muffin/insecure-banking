"""Initial migration for transfers app."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for transfers app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transfer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fromAccount", models.CharField(max_length=80)),
                ("toAccount", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=80)),
                ("amount", models.FloatField()),
                ("fee", models.FloatField(default=20)),
                ("username", models.CharField(max_length=80)),
                ("date", models.DateTimeField()),
            ],
            options={
                "db_table": "web_transfer",
                "verbose_name": "Transfer",
                "verbose_name_plural": "Transfers",
            },
        ),
    ]
