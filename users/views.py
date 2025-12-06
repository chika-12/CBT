from django.shortcuts import render, redirect
from . import models
from . import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .utils import get_client_ip
from .utils import annotate_login_history_with_location

# Create your views here.

def indexPage(request):
  return render(request, "index.html")


@login_required
def profile(request):
  try:
    profile = models.Profile.objects.get(user=request.user)
  except models.Profile.DoesNotExist:
    profile = None
  return render(request, "profile.html", {"profile": profile})

def signupPage(request):
  return render(request, "signup.html")


@api_view(["POST"])
def signup(request):
  email = request.data.get("email")
  password = request.data.get("password")
  confirm_password = request.data.get("confirm_password")

  if not password:
    messages.error(request, "Password required")
    return Response("signup_page")
  if not email:
    messages.error(request, "Email required")
    return redirect("signup_page")
  
  if password != confirm_password:
    messages.error(request, "Passwords do not match")
    redirect("signup_page")
  
  data = serializers.UserSerializers(data=request.data)
  if data.is_valid():
    user = data.save()
    login(request, user)
    messages.success(request, "Signup successful! Welcome to your profile.")
    return redirect("profile")
  messages.error(request, "Something went wrong")
  print(data.errors)
  return redirect("signup_page")

@login_required
def edit_profile(request):
  profile = models.Profile.objects.get(user=request.user)
    
  if request.method == "POST":
    profile.name = request.POST.get("name")
    profile.city = request.POST.get("city")
    profile.state = request.POST.get("state")
    profile.address = request.POST.get("address")
    profile.bio = request.POST.get("bio")
    profile.save()
    messages.success(request, "Profile updated successfully!")
    return redirect("profile")

  return render(request, "edit_profile.html", {"profile": profile})

def delete(request):
  user = request.user
  user.delete() # To be updated later
  messages.success(request, "Your account has been deleted successfully.")
  return redirect("signup_page") 


def login_page(request):
  if request.method == "POST":
    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(request, email=email, password=password)

    if user is not None:
      login(request, user)

      ip = get_client_ip(request)
      user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
      models.LoginHistory.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent
      )
      messages.success(request, f"Welcome back, {user.first_name}!")
      return redirect("profile")  # redirect to profile page
    else:
      messages.error(request, "Invalid email or password")
      return redirect("login_page")

  return render(request, "login.html")

from django.contrib.auth import logout

def logout_view(request):
  logout(request)
  messages.success(request, "You have been logged out successfully.")
  return redirect("login_page")



def getLoginHistory(request):
  if request.method == "GET":
    history = models.LoginHistory.objects.all()
    history = annotate_login_history_with_location(history)
    return render(request, "login_history.html", {"history": history})