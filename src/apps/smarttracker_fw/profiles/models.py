from django.contrib.auth.models import User
from django.db import models


class BaseProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="%(class)s_profile"
    )
    remind_interval_hours = models.PositiveSmallIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
