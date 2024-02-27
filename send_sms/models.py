from django.db import models
from django.utils import timezone

class SmsInfos(models.Model):
    """Table which save data from generator commands"""
    tab_id = models.TextField(max_length=150, primary_key=True)
    source_gpon = models.JSONField(null=True)
    unchanged_devices = models.TextField(null=True)
    selected_devices = models.TextField(null=True)
    contacts = models.JSONField(null=True)
    rupture = models.JSONField(null=True)
    sms_result = models.JSONField(null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True)
