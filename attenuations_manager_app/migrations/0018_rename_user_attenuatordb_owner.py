# Generated by Django 4.2.5 on 2024-06-07 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attenuations_manager_app', '0017_attenuatordb_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attenuatordb',
            old_name='user',
            new_name='owner',
        ),
    ]
