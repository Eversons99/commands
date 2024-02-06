# Generated by Django 4.2.5 on 2024-01-30 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands_generator', '0011_alter_generatordb_commands_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatordb',
            name='commands_url',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='destination_gpon',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='file_name',
            field=models.TextField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='selected_devices',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='source_gpon',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='generatordb',
            name='unchanged_devices',
            field=models.TextField(null=True),
        ),
    ]