from django.db import models
from django.utils import timezone

class AttenuatorDB(models.Model):
    """
    Table which save data from attenuations manager
    """
    register_id = models.TextField(max_length=150, primary_key=True)
    owner = models.TextField(max_length=150, null=True)
    file_name = models.TextField(max_length=150, null=True)
    source_gpon = models.JSONField(null=True)
    destination_gpon = models.JSONField(null=True)
    unchanged_onts = models.TextField(null=True)
    selected_devices = models.TextField(null=True)
    commands_url = models.JSONField(null=True)
    rollback_commands_url = models.JSONField(null=True)
    rollback_logs = models.JSONField(null=True)
    attenuations = models.JSONField(null=True)
    logs = models.JSONField(null=True)
    commands_applied = models.BooleanField(default=False)
    rollback_commands_applied = models.BooleanField(default=False)
    date_commands_applied = models.DateTimeField(null=True)
    date_rollback_commands_applied = models.DateTimeField(null=True)
    commands_removed = models.BooleanField(default=False)
    source_port_config = models.TextField(null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True)
