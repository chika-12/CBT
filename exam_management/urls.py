from django.urls import path
from . import views

urlpatterns = [
  path("add_teacher/", views.create_teacher, name="add_teacher"),
  path("remove_teacher/", views.remove_teacher, name="remove_teacher"),
  path("list_teachers/", views.list_all_teachers, name="all_teachers"),
  path("update_teacher/", views.update_teacher, name="update_teacher"),
  path("teacher_dashboard/", views.teachers_dashboard, name="teacher_dashboard"),
  path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
  path("system_setting/", views.system_setting, name="system_settings"),
  path("user_managemnt/", views.user_management, name="user_management"),
  path("report_analytics/", views.report_analytics, name="reports_analytics"),
  path("system_health/", views.system_health, name="system_health"),
  path("audit_logs/", views.audit_logs, name="audit_logs")
]