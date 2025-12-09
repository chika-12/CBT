from django.shortcuts import render, redirect
from . import models
from . import serializers
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
User = get_user_model()
# Create your views here.

@login_required
def create_teacher(request):
  if request.method == "POST":

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
def list_all_teachers(request):
  if request.method == "GET":
    teachers = models.Teacher.objects.all()
    serialized = serializers.Teacher(teachers, many=True)
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


