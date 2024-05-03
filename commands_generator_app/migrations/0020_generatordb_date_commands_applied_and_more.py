# Generated by Django 4.2.5 on 2024-05-02 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands_generator_app', '0019_generatordb_commands_applied_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatordb',
            name='date_commands_applied',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='generatordb',
            name='date_rollback_commands_applied',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='commands_applied',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='rollback_commands_applied',
            field=models.BooleanField(default=False),
        ),
    ]
