import uuid

from django.db import models

class Stamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    removed_at = models.DateTimeField(null=True, default=None)
    count = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class CLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE)
    stamped_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.stamp.name
