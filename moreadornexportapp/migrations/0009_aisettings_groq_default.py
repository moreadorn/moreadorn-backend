"""Switch the AiSettings provider/model defaults from Gemini → Groq.

Also migrates any existing row that's still on the old Gemini values so
the live chat doesn't break the moment the new schema is deployed.
"""

from django.db import migrations, models


def gemini_to_groq(apps, schema_editor):
    AiSettings = apps.get_model("moreadornexportapp", "AiSettings")
    AiSettings.objects.filter(provider="gemini").update(provider="groq")
    AiSettings.objects.filter(model_name__startswith="gemini").update(
        model_name="llama-3.3-70b-versatile",
    )


def noop(apps, schema_editor):  # pragma: no cover — irreversible by design
    """Reverse migration is intentionally a no-op. We don't want to put a
    deprecated model name back into the row."""


class Migration(migrations.Migration):

    dependencies = [
        ("moreadornexportapp", "0008_emailconfig"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aisettings",
            name="provider",
            field=models.TextField(
                choices=[("groq", "Groq")],
                default="groq",
            ),
        ),
        migrations.AlterField(
            model_name="aisettings",
            name="model_name",
            field=models.TextField(default="llama-3.3-70b-versatile"),
        ),
        migrations.RunPython(gemini_to_groq, noop),
    ]
