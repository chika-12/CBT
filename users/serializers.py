from rest_framework import serializers
from . import models
class UserSerializers(serializers.ModelSerializer):
  class Meta:
    model = models.User
    fields = ["id","first_name", "last_name", "email", "password"]
    extra_kwargs = {"password": {"write_only": True}}

  def create(self, validated_data):
    password = validated_data.pop("password")
    user = models.User(**validated_data)
    user.set_password(password)
    user.role = 'admin'
    user.save()
    return user

class ProfileSerialzer(serializers.ModelSerializer):
  class Meta:
    model = models.Profile
    fields = "__all__"

class LoginHistorySerializer(serializers.ModelSerializer):
  user = UserSerializers(read_only=True)
  class Meta:
    model = models.LoginHistory
    fields = "__all__"