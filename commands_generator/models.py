from datetime import datetime
from django.db import models
from django.utils import timezone

class MaintenanceInfo(models.Model):
    """Table which save data from generator commands"""
    tab_id = models.TextField(max_length=150, primary_key=True)
    file_name = models.TextField(max_length=150, null=True)
    source_gpon = models.JSONField(null=True)
    destination_gpon = models.JSONField(null=True)
    unchanged_devices = models.TextField(null=True)
    selected_devices = models.TextField(null=True)
    commands_url = models.JSONField(null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True)
