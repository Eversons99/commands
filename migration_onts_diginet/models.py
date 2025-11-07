from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class DiginetOntsMigrationDB(models.Model):
    """
    Table which save data from attenuations manager
    """
    register_id = models.TextField(max_length=150, primary_key=True)
    pon = models.TextField(max_length=150, null=False)
    host = models.TextField(max_length=150, null=False)
    serial_numbers = ArrayField(models.CharField(max_length=50),blank=True,default=list)
    created_date = models.DateTimeField(default=timezone.now, null=True)
