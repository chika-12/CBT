from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_books, name="add-book"),
    path("list/", views.list_book, name="book-list"),
    path("management/", views.book_management, name="book_management"),
    path("borrow/", views.borrow_management, name="borrow_management")
]