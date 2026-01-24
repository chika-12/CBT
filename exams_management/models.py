from django.db import models

# Create your models here.
from django.conf import settings
import uuid
# Create your models here.

class Test(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  subject = models.CharField(max_length=230)
  teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  description = models.TextField(blank=True, null=True)
  class_level = models.CharField(blank=False, null=False, max_length=280, default="No Class")# new feature
  time_limit = models.IntegerField(default=60)
  is_published = models.BooleanField(default=False)
  date_added = models.DateTimeField(auto_now_add=True)
  date_updated = models.DateTimeField(auto_now=True)

  @property
  def total_questions(self):
    return self.questions.count()

  


class Questions(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  test = models.ForeignKey("Test", on_delete=models.CASCADE, related_name="questions")
  question_text = models.CharField(max_length=500)
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


class StudentTestAttempt(models.Model):
  student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  test = models.ForeignKey('Test', on_delete=models.CASCADE)
  start_time = models.DateTimeField(auto_now_add=True)
  end_time = models.DateTimeField(null=True, blank=True)
  is_completed = models.BooleanField(default=False)
  total_score = models.IntegerField(default=0)
  earned_score = models.IntegerField(default=0)
  percentage = models.FloatField(default=0)
    
  class Meta:
    unique_together = ['student', 'test']

class StudentAnswer(models.Model):
  attempt = models.ForeignKey(StudentTestAttempt, on_delete=models.CASCADE)
  question = models.ForeignKey('Questions', on_delete=models.CASCADE)
  selected_choice = models.ForeignKey('Choice', on_delete=models.CASCADE, null=True, blank=True)
  # For multiple choice questions, you might want a ManyToManyField:
  # selected_choices = models.ManyToManyField('Choice')
    
  class Meta:
    unique_together = ['attempt', 'question']