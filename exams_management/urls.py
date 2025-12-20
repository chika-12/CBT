# exam_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
  # =============== TEST MANAGEMENT ===============
  # List all tests
  path('tests/', views.test_list, name='test_list'),
   
  # Create test (GET shows form, POST processes it)
  path('tests/create/', views.test_create, name='test_create'),
    
  # Update test (GET shows form, POST processes update) - CHANGED to <str:test_id>
  path('tests/<str:test_id>/update/', views.test_update, name='test_update'),
    
  # Delete test (GET shows confirmation, POST processes delete) - CHANGED to <str:test_id>
  path('tests/<str:test_id>/delete/', views.test_delete, name='test_delete'),
    
  # Publish/unpublish test - CHANGED to <str:test_id>
  path('tests/<str:test_id>/publish/', views.test_publish, name='test_publish'),
   
    
  # =============== QUESTION MANAGEMENT ===============
  # List questions for a test - CHANGED to <str:test_id>
  path('tests/<str:test_id>/questions/', views.question_list, name='question_list'),
    
  # Create question for a test - CHANGED to <str:test_id>
  path('tests/<str:test_id>/questions/create/', views.question_create, name='question_create'),
   
  # Update question
  path('questions/<str:question_id>/update/', views.question_update, name='question_update'),
    
  # Delete question
  path('questions/<str:question_id>/delete/', views.question_delete, name='question_delete'),
    
    
  # =============== CHOICE MANAGEMENT ===============
  # List choices for a question
  path('questions/<str:question_id>/choices/', views.choice_list, name='choice_list'),
    
  # Create choice for a question
  path('questions/<str:question_id>/choices/create/', views.choice_create, name='choice_create'),
    
  # Update choice
  path('choices/<str:choice_id>/update/', views.choice_update, name='choice_update'),
    
  # Delete choice
  path('choices/<str:choice_id>/delete/', views.choice_delete, name='choice_delete'),
]