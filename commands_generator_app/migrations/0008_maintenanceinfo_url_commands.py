# Generated by Django 4.2.5 on 2023-10-30 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands_generator_app', '0007_maintenanceinfo_selected_devices'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenanceinfo',
            name='url_commands',
            field=models.JSONField(null=True),
        ),
    ]
