import uuid

from django.db import models

class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32, unique=True, null=True)
    def __str__ (self):
        return self.name

class Stamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(null=True)
    count = models.IntegerField(default=0)
    tag = models.CharField(max_length=128, default="normal")
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

class CLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    stamp = models.ForeignKey(Stamp, on_delete=models.CASCADE)
    stamped_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.stamp.name

