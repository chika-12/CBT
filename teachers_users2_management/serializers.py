from rest_framework import serializers
from . import models
from users.serializers import UserSerializers
class TeacherSerializer(serializers.ModelSerializer):
  user = UserSerializers(read_only=True)
  class Meta:
    model = models.Teacher
    fields = "__all__"

class StudentSerializer(serializers.ModelSerializer):
  user = UserSerializers(read_only=True)
  class Meta:
    model = models.Student
    fields = "__all__"