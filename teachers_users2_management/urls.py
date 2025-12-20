from django.urls import path
from . import views

urlpatterns = [
  path("add_teacher/", views.create_teacher, name="add_teacher"),
  path("remove_teacher/", views.remove_teacher, name="remove_teacher"),
  path("list_teachers/", views.list_all_teachers, name="all_teachers"),
  path("update_teacher/", views.update_teacher, name="update_teacher"),
  path("teacher_dashboard/", views.teachers_dashboard, name="teacher_dashboard"),
  path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
  path("system_setting/", views.system_setting, name="system_settings"), # yet to be built
  path("user_managemnt/", views.user_management, name="user_management"),
  path("report_analytics/", views.report_analytics, name="reports_analytics"), # yet to be built
  path("system_health/", views.system_health, name="system_health"), # yet to be built
  path("audit_logs/", views.audit_logs, name="audit_logs"), # yet to be built
  path("add_student/", views.make_student, name="add_student"),
  path("students_dashboard", views.students_dashboard, name="students_dashboard"),
  path("system/delete-user/<str:user_id>/", views.delete_user_by_id, name="delete_user"),


  path('exams/', views.exam_list, name='exam_list'),
  path('results/', views.student_results, name='student_results'),
  path('payment/', views.payment_page, name='payment_page'),
  path('payment/history/', views.payment_history, name='payment_history'),
  path('library/', views.library, name='library'),
  path('library/borrowed/', views.borrowed_books, name='borrowed_books'),
  path('report-issue/', views.report_issue, name='report_issue'),
  path('issues/', views.view_issues, name='view_issues'),
  path('help/', views.help_center, name='help_center'),
  #path('settings/', views.settings, name='settings'),
  #path('logout/', views.logout_view, name='logout'),
]