from django.urls import path
from . import views

urlpatterns = [
  path("add_teacher", views.create_teacher, name="add_teacher"),
  path("remove_teacher/", views.remove_teacher, name="remove_teacher"),
  path("list_teachers", views.list_all_teachers, name="all_teachers"),
  path("update_teacher", views.update_teacher, name="update_teacher"),
]