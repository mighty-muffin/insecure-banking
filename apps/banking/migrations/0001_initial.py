"""Initial migration for banking app."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for banking app."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CashAccount",
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
                ("number", models.CharField(max_length=80)),
                ("username", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=80)),
                ("availableBalance", models.FloatField()),
            ],
            options={
                "db_table": "web_cashaccount",
                "verbose_name": "Cash Account",
                "verbose_name_plural": "Cash Accounts",
            },
        ),
        migrations.CreateModel(
            name="CreditAccount",
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
                ("cashAccountId", models.IntegerField()),
                ("number", models.CharField(max_length=80)),
                ("username", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=80)),
                ("availableBalance", models.FloatField()),
            ],
            options={
                "db_table": "web_creditaccount",
                "verbose_name": "Credit Account",
                "verbose_name_plural": "Credit Accounts",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("number", models.CharField(max_length=80)),
                ("description", models.CharField(max_length=80)),
                ("amount", models.FloatField()),
                ("availableBalance", models.FloatField()),
                ("date", models.DateTimeField()),
            ],
            options={
                "db_table": "web_transaction",
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
            },
        ),
    ]
