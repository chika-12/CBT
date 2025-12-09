from django.db import models
from django.conf import settings
import uuid
# Create your models here.

class Test(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  subject = models.CharField(max_length=230)
  teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  description = models.TextField(blank=True)
  total_questions = models.IntegerField(default=0)
  time_limit = models.IntegerField(default=60, help_text="Time limit in minutes")  # Optional
  is_published = models.BooleanField(default=False)
  date_added = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(auto_now=True)
  def save(self, *args, **kwargs):
    # Update total questions count
    self.total_questions = self.questions.count()
    super().save(*args, **kwargs)
  
  def __str__(self):
    return f"{self.subject} ({self.teacher.username})"
  
  


class Questions(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  test = models.ForeignKey("Test", on_delete=models.CASCADE, related_name="questions")
  question_text = models.CharField(max_length=500)  # Increased length
  question_type = models.CharField(
      max_length=20,
      choices=[('single', 'Single Choice'), ('multiple', 'Multiple Choice')],
      default='single'
    )
  marks = models.IntegerField(default=1)  # Marks for this question
  explanation = models.TextField(blank=True, help_text="Explanation for correct answer")  # Optional
  order = models.IntegerField(default=0, help_text="Order in test")
  date_added = models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering = ['order', 'date_added']
    
  def __str__(self):
    return f"Q{self.order}: {self.question_text[:50]}..."


class Choice(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  question = models.ForeignKey("Questions", on_delete=models.CASCADE, related_name="choices")
  choice_text = models.CharField(max_length=280)
  is_correct = models.BooleanField(default=False)
  order = models.IntegerField(default=0)
  date_added = models.DateTimeField(auto_now_add=True)
    
  class Meta:
    ordering = ['order', 'date_added']
    
  def __str__(self):
    return f"{self.choice_text[:30]}... ({'✓' if self.is_correct else '✗'})"


class Teacher(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  subject = models.CharField(max_length=230)
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(auto_now=True)

class Student(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(default=True)