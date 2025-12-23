from django.urls import path
from . import views
urlpatterns = [
  path("", views.indexPage, name="indexPage"),
  path("signup/", views.signupPage, name="signup_page"),
  path("signup/submit/", views.signup, name="signup"),
  path("profile/edit/", views.edit_profile, name="edit_profile"),
  path("delete/", views.delete, name="delete"),
  path("profile/", views.profile, name="profile"),
  path("login/", views.login_page, name="login_page"),
  path("logout/", views.logout_view, name="logout"),
  path("login_history/", views.getLoginHistory, name="login_history"),
  path("vision-bearer/", views.vision_bearer_page, name="vision_bearer"),

]