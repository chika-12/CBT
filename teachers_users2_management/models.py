from django.db import models
from django.conf import settings
import uuid

class Teacher(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  subject = models.CharField(max_length=230)
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(auto_now=True)

class Student(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  class_level = models.CharField(blank=False, null=False, max_length=280, default="No Class") #new feature
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(auto_now=True)