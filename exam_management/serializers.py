from rest_framework import serializers
from . import models
from users.serializers import UserSerializers
class TestSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.Test
    fields = ["id", "subject"]

class QuestionsSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.Questions
    fields = ["id", "test", "question_text"]

class ChoiceSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.Choice
    fields = ["id", "choice_text", "question", "is_correct"]

class Teacher(serializers.ModelSerializer):
  user = UserSerializers(read_only=True)
  class Meta:
    model = models.Teacher
    fields = ["user", "subject"]