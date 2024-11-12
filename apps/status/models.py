from django.db import models

class StatusModel(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    class Meta:
        permissions = [
            ("can_change_status_only", "Can only change field status"),
        ]

    def __str__(self):
        return self.name
