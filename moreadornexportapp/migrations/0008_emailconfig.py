import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("moreadornexportapp", "0007_remove_aiapikey_provider"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailConfig",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "label",
                    models.TextField(
                        help_text="Human-friendly name, e.g. 'Production Gmail'.",
                    ),
                ),
                (
                    "email",
                    models.TextField(
                        help_text="The Gmail / SMTP address that emails are sent from.",
                    ),
                ),
                (
                    "app_password",
                    models.TextField(
                        help_text="Gmail app password (or SMTP password). Stored encrypted-at-rest by the DB.",
                    ),
                ),
                ("host", models.TextField(default="smtp.gmail.com")),
                ("port", models.IntegerField(default=587)),
                ("use_tls", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Email Config",
                "verbose_name_plural": "Email Configs",
                "ordering": ["-created_at"],
            },
        ),
    ]
