from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import uuid

# Create your models here.
class ActiveManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(is_active=True)
  

class UserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError("Email required")
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user
  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)

    if extra_fields.get("is_staff") is not True:
      return ValueError("Superuser must have is_staff set to True")
    if extra_fields.get("is_superuser") is not True:
      return ValueError("Superuser must have superuser set to True")
    return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  STATUS_ROLE = [
    ("student", "Student"),
    ("teacher", "Teacher"),
    ("admin", "Admin")
  ]
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  first_name = models.CharField(max_length=230)
  last_name = models.CharField(max_length=230)
  email = models.EmailField(unique=True)
  role = models.CharField(max_length=230, choices=STATUS_ROLE)
  is_active = models.BooleanField(default=True)
  date_added = models.DateField(auto_now=True)

  objects = UserManager()
  active = ActiveManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["first_name", "last_name"]

class Profile(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey("User", on_delete=models.CASCADE)
  name = models.CharField(max_length=230)
  name_of_School = models.CharField(max_length=230, default="Karmo Development Center")
  state = models.CharField(max_length=230, default="FCT Abuja")
  city = models.CharField(max_length=230, default="Amac")
  address = models.CharField(max_length=230)
  bio = models.TextField()
  role = models.CharField(max_length=230, null=True, blank=True)
  date_added = models.DateField(auto_now=True)


class LoginHistory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  ip_address = models.GenericIPAddressField()
  user_agent = models.TextField()
  timestamp = models.DateTimeField(auto_now_add=True)
