# Generated by Django 4.2.9 on 2024-01-19 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('send_sms', '0004_smsinfos_rupture_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smsinfos',
            name='rupture_id',
        ),
        migrations.AddField(
            model_name='smsinfos',
            name='rupture',
            field=models.JSONField(null=True),
        ),
    ]