from django.shortcuts import render, redirect
from . import models
from . import serializers
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
User = get_user_model()
from users.models import Profile
# Create your views here.

@login_required
def create_teacher(request):
  if request.method == "POST":
    if request.user.role != "admin":
      messages.error(request, "Unauthorized action")
      return redirect("profile")

    email = request.POST.get("email")
    subject = request.POST.get("subject")
    if not email:
      messages.error(request, "Email required")
      return redirect("profile")
    if not subject:
      messages.error(request, "Subject required")
      return redirect("profile")
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User not found")
      return redirect("profile")
    
    if models.Teacher.objects.filter(user=user).exists():
      messages.warning(request, "This user is already a teacher")
      return redirect("profile")

    models.Teacher.objects.create(user=user, subject=subject)
    user_profile = Profile.objects.get(user=user)
    user_profile.role = "teacher"
    user_profile.save()
    messages.success(request, "Action Successfull")
    return redirect("profile")
  return render(request, "add_teacher.html")

@login_required
def remove_teacher(request):
  if request.method == "POST":
    email = request.POST.get("email")
    if request.user.role != "admin":
      messages.error(request, "Unauthorized action")
      return redirect("profile")
    
    if not email:
      messages.error(request, "Email required")
      return redirect("profile")
    
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User does not exist")
      return redirect("profile")
    
    try:
      teacher = models.Teacher.objects.filter(user=user)
    except models.Teacher.DoesNotExist:
      messages.error(request, "No teacher with such email or teacher not found")
      return redirect("profile")
    
    teacher.delete()
    messages.success(request, "Teacher deleted successfully")
    return redirect("profile")
  return render(request, "delete_teacher.html")


@login_required
def admin_dashboard(request):
  if Profile.objects.get(user=request.user).role != "admin":
    messages.error(request, "Access Denied")
    return redirect("profile")
  try:
    user = Profile.objects.get(user=request.user)
  except User.DoesNotExist:
    user = None
  return render(request, "admin_dashboard.html", {"user":user})

@login_required
def teachers_dashboard(request):
  if Profile.objects.get(user=request.user).role != "teacher":
    messages.error(request, "You can not access this dashboard")
    return redirect("profile")
  try:
    teacher = models.Teacher.objects.get(user=request.user)
  except models.Teacher.DoesNotExist:
    teacher = None
  return render(request, "teachers_dashboard.html", {"teacher": teacher})

@login_required
def list_all_teachers(request):
  if request.method == "GET":
    if request.user.role != "admin":
      messages.error(request, "Unauthorized action")
      return redirect("profile")
    teachers = models.Teacher.objects.all()
    serialized = serializers.TeacherSerializer(teachers, many=True)
    return render(request, "all_teachers.html", {"teachers": serialized.data})

@login_required
def update_teacher(request):
  if request.method == "POST":
    if request.user.role != "admin":
      messages.error(request, "You dont have permision to perform this action")
      return redirect("profile")
    email = request.POST.get("email")
    subject = request.POST.get("subject")
    if not email:
      messages.error(request, "Email required")
      return redirect("profile")
    if not subject:
      messages.error(request, "Subject required")
      return redirect("profile")
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User not found")
      return redirect("profile")
    teacher = models.Teacher.objects.get(user=user)
    teacher.subject = subject
    teacher.save()
    messages.success(request, "Action Successfull", extra_tags='alert-success')
    return redirect("profile")
  return render(request, "update_teacher.html")





def system_setting(request):
  pass

def user_management(request):
  pass

def report_analytics(request):
  pass

def system_health(request):
  pass
def audit_logs(request):
  pass


"""
The CBT portal begins from below
"""

def add_test(request):
  subject = request.POST.get("subject")
