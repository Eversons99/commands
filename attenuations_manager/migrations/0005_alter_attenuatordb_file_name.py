# Generated by Django 4.2.5 on 2024-01-30 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attenuations_manager', '0004_alter_attenuatordb_attenuations_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attenuatordb',
            name='file_name',
            field=models.TextField(max_length=150, null=True),
        ),
    ]