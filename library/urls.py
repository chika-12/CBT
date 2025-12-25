from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_books, name="add-book"),
    path("list/", views.list_book, name="book-list"),
    path("management/", views.book_management, name="book_management"),
    path("borrow/", views.borrow_management, name="borrow_management"),
    path("read-book/<str:bookId>/", views.read_book, name="read_book"),
    path('suggest-book/', views.suggest_book, name='suggest_book'),
    path('admin/suggestions/', views.admin_view_suggested_books, name='view_suggested_books'),
    path('admin/suggestions/update/<str:suggestion_id>/',views.update_suggestion_status,name='update_suggestion_status'),
]