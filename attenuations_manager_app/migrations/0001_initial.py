# Generated by Django 4.2.5 on 2024-01-30 00:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AttenuatorDB",
            fields=[
                (
                    "tab_id",
                    models.TextField(max_length=150, primary_key=True, serialize=False),
                ),
                ("file_name", models.TextField(max_length=150, null=True)),
                ("source_gpon", models.JSONField(null=True)),
                ("destination_gpon", models.JSONField(null=True)),
                ("unchanged_devices", models.TextField(null=True)),
                ("selected_devices", models.TextField(null=True)),
                ("commands_url", models.JSONField(null=True)),
                ("search_mode", models.TextField(null=True)),
                ("attenuations", models.JSONField(null=True)),
                (
                    "created_date",
                    models.DateTimeField(default=django.utils.timezone.now, null=True),
                ),
            ],
        ),
    ]
