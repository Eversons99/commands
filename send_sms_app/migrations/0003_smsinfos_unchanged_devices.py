# Generated by Django 4.2.9 on 2024-01-18 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('send_sms_app', '0002_remove_smsinfos_unchanged_devices_smsinfos_contacts'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsinfos',
            name='unchanged_devices',
            field=models.TextField(null=True),
        ),
    ]