from rest_framework import serializers
from . import models
from users.serializers import UserSerializers
class TestSerializers(serializers.ModelSerializer):
  teacher_name = serializers.SerializerMethodField()
  status_display = serializers.SerializerMethodField()
  total_questions = serializers.SerializerMethodField() 

  class Meta:
    model = models.Test
    fields = [
      "id", 
      "subject", 
      "teacher", 
      "teacher_name",
      "description",
      "total_questions", 
      "time_limit", 
      "is_published",
      "status_display",
      "date_added",
      "date_updated"
    ]
    read_only_fields = [
      "id", 
      "teacher",
      "date_added", 
      "date_updated"
    ]
  
  def get_teacher_name(self, obj):
    """Get teacher's full name or username"""
    if obj.teacher.get_full_name():
      return obj.teacher.get_full_name()
    return obj.teacher.username
  
  def get_status_display(self, obj):
    """Human-readable status"""
    return "Published" if obj.is_published else "Draft"
  
  def validate_time_limit(self, value):
    """Custom validation for time limit"""
    if value < 1:
      raise serializers.ValidationError("Time limit must be at least 1 minute")
    if value > 480:  # 8 hours max
      raise serializers.ValidationError("Time limit cannot exceed 8 hours")
    return value
  
  def validate_subject(self, value):
    """Validate subject field"""
    if len(value.strip()) < 2:
      raise serializers.ValidationError("Subject must be at least 2 characters")
    return value.strip()
  
  def create(self, validated_data):
    """Override create to set teacher automatically"""
    request = self.context.get('request')
    if request and hasattr(request, 'user'):
      validated_data['teacher'] = request.user
    return super().create(validated_data)


class QuestionsSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.Questions
    fields = "__all__"

class ChoiceSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.Choice
    fields = "__all__"
