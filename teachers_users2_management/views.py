from django.shortcuts import render, redirect
from . import models
from . import serializers
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
User = get_user_model()
from users.models import Profile
from users.serializers import UserSerializers
from django.views.decorators.http import require_POST
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
      return redirect("add_teacher")
    if not subject:
      messages.error(request, "Subject required")
      return redirect("add_teacher")
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User not found")
      return redirect("admin_dashboard")
    
    if user.role == "admin":
      messages.error(request, "You cant make an admin a teacher")
      return redirect("admin_dashboard")
    
    if models.Teacher.objects.filter(user=user).exists():
      messages.warning(request, "This user is already a teacher")
      return redirect("admin_dashboard")

    models.Teacher.objects.create(user=user, subject=subject)
    user_profile = Profile.objects.get(user=user)
    user_profile.role = "teacher"
    user.role = "teacher"
    user.save()
    user_profile.save()
    messages.success(request, "Action Successfull")
    return redirect("admin_dashboard")
  return render(request, "add_teacher.html")

@login_required
def remove_teacher(request):
  if request.method == "POST":
    email = request.POST.get("email")
    if request.user.role != "admin":
      messages.error(request, "Unauthorized action")
      return redirect("admin_dashboard")
    
    if not email:
      messages.error(request, "Email required")
      return redirect("admin_dashboard")
    
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User does not exist")
      return redirect("admin_dashboard")
    
    try:
      teacher = models.Teacher.objects.filter(user=user)
    except models.Teacher.DoesNotExist:
      messages.error(request, "No teacher with such email or teacher not found")
      return redirect("admin_dashboard")
    
    teacher.delete()
    messages.success(request, "Teacher deleted successfully")
    return redirect("admin_dashboard")
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
def students_dashboard(request):
  if Profile.objects.get(user=request.user).role != "student":
    messages.error(request, "Access Denied")
    return redirect("profile")
  try:
    user = models.Student.objects.get(user=request.user)
  except User.DoesNotExist:
    user = None
  return render(request, "students_dashboard.html", {"user":user})

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
      return redirect("update_teacher")
    if not subject:
      messages.error(request, "Subject required")
      return redirect("update_teacher")
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User not found")
      return redirect("admin_dashboard")
    teacher = models.Teacher.objects.get(user=user)
    teacher.subject = subject
    teacher.save()
    messages.success(request, "Action Successfull", extra_tags='alert-success')
    return redirect("admin_dashboard")
  return render(request, "update_teacher.html")





def system_setting(request):
  pass



def user_management(request):
    if request.method == "GET":
        # Check if user is admin
        try:
            user_profile = Profile.objects.get(user=request.user)
            if user_profile.role != "admin":
                messages.error(request, "Access Denied")
                return redirect("admin_dashboard")
        except Profile.DoesNotExist:
            messages.error(request, "Profile not found")
            return redirect("admin_dashboard")

        # Get all users (FIXED: use date_added instead of date_joined)
        users = User.objects.all().order_by('-date_added')

        # Serialize users
        users_data = UserSerializers(users, many=True).data

        processed_users = []
        colors = ["#4361ee", "#3a0ca3", "#4cc9f0", "#f72585", "#7209b7", "#560bad"]

        for i, user_dict in enumerate(users_data):
            user_id = str(user_dict.get('id'))
            #user_id = user_dict.get('id')
            email = user_dict.get('email')
            first_name = user_dict.get('first_name', '')
            last_name = user_dict.get('last_name', '')

            # You do NOT have username → remove it
            username = email.split("@")[0] if email else "user"

            # Name
            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            else:
                name = username

            # Initials
            if first_name and last_name:
                initials = f"{first_name[0]}{last_name[0]}"
            elif first_name:
                initials = first_name[0]
            else:
                initials = username[0].upper()

            # Role, status, join date
            try:
                user_obj = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user_obj)

                role = profile.role
                status = "active" if user_obj.is_active else "inactive"

                # FIXED: use date_added instead of date_joined
                join_date = user_obj.date_added.strftime("%d %b %Y") if user_obj.date_added else "Unknown"
                last_login = user_obj.last_login.strftime("%d %b %Y") if user_obj.last_login else "Never"

            except:
                role = "user"
                status = "active"
                join_date = "Unknown"
                last_login = "Never"

            # Append processed user (FIXED indentation)
            processed_users.append({
                'id': user_id,
                'name': name,
                'email': email,
                'username': username,
                'role': role,
                'status': status,
                'avatar_color': colors[i % len(colors)],
                'initials': initials,
                'join_date': join_date,
                'last_login': last_login,
            })

        # System statistics
        total_users = users.count()
        active_users = users.filter(is_active=True).count()
        admin_count = Profile.objects.filter(role="admin").count()

        context = {
            'users': processed_users,
            'total_users': total_users,
            'active_users': active_users,
            'admin_count': admin_count,
        }

        return render(request, "all_users.html", context)



@require_POST
def delete_user_by_id(request, user_id):
  try:
    user = User.objects.get(id=user_id)
  except User.DoesNotExist:
    messages.error(request, "No user found")
    return redirect("user_managemen")
  user.delete()
  messages.success(request, "User deleted successfully")
  return redirect("user_management")
  
  
def make_student(request):
  if request.method == "POST":
    if request.user.role != "admin":
      messages.error(request, "Unauthorized action")
      return redirect("profile")

    email = request.POST.get("email")
    if not email:
      messages.error(request, "Email required")
      return redirect("admin_dashboard")
    
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      messages.error(request, "User does not exist")
      return redirect("admin_dashboard")
    
    models.Student.objects.create(user=user)
    user.role = "student"
    std_profile = Profile.objects.get(user=user)
    std_profile.role = "student"
    user.save()
    std_profile.save()
    messages.success(request, "Action Successfull")
    return redirect("admin_dashboard")
  return render(request, "add_student.html")


def report_analytics(request):
  pass

def system_health(request):
  pass
def audit_logs(request):
  pass






def exam_list(request):
    pass


def student_results(request):
    pass


def payment_page(request):
    pass


def payment_history(request):
    pass


def library(request):
    pass


def borrowed_books(request):
    pass


def report_issue(request):
    pass


def view_issues(request):
    pass


def help_center(request):
    pass


def settings(request):
    pass


def logout_view(request):
    pass
