# Generated by Django 4.2.5 on 2024-04-03 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands_generator_app', '0014_generatordb_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatordb',
            name='original_configuration',
            field=models.TextField(null=True),
        ),
    ]
