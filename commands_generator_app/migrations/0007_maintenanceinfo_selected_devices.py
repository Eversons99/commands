# Generated by Django 4.2.5 on 2023-10-30 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands_generator_app', '0006_rename_maintenceinfo_maintenanceinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenanceinfo',
            name='selected_devices',
            field=models.TextField(null=True),
        ),
    ]