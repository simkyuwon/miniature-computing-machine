from django.db import models
import uuid


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    parent = models.ForeignKey("Folder", blank=True, null=True, on_delete=models.CASCADE, db_column="parent")

    def __str__(self):
        return f'{self.name}:{self.id}'


def file_path(instance, filename):
    return f'file/{instance.id}'


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    contents = models.FileField(upload_to=file_path, blank=True)
    group_size = models.IntegerField(default=0, blank=False, null=False)
    parent = models.ForeignKey("Folder", blank=True, null=True, on_delete=models.CASCADE, db_column="parent")

    def __str__(self):
        return f'{self.title}:{self.id}'
