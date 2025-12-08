from django.db import models
from django.conf import settings
import uuid
# Create your models here.

class Test(models.Model):
  id = models.UUIDField(primary_key=True, default=True, editable=False)
  subject = models.CharField(max_length=230)
  date_added = models.DateField(auto_now=True)

class Questions(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  test = models.ForeignKey("Test", on_delete=models.CASCADE, related_name="questions")
  question_text = models.CharField(max_length=230)
  date_added = models.DateField(auto_now=True)


class Choice(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  questions = models.ForeignKey("Questions", on_delete=models.CASCADE, related_name="choices")
  choice_text = models.CharField(max_length=280)
  is_correct = models.BooleanField(default=False)
  date_added = models.DateField(auto_now=True)

class Teacher(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  subject = models.CharField(max_length=230)
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(auto_now=True)
