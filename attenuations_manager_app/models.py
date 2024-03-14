from django.db import models
from django.utils import timezone

class AttenuatorDB(models.Model):
    """
    Table which save data from attenuations manager
    """
    register_id = models.TextField(max_length=150, primary_key=True)
    file_name = models.TextField(max_length=150, null=True)
    source_gpon = models.JSONField(null=True)
    destination_gpon = models.JSONField(null=True)
    unchanged_onts = models.TextField(null=True)
    selected_devices = models.TextField(null=True)
    commands_url = models.JSONField(null=True)
    attenuations = models.JSONField(null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True)
