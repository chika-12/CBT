from django.shortcuts import render, redirect, get_list_or_404
from django.contrib import messages
from . import models
from .serializer import BookForm
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


@login_required
def add_books(request):
    """View to add new books (admin only)."""
    form = BookForm()
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("profile")
    if profile.role != "admin":
        messages.error(request, "Unauthorized Action. Admin access required.")
        return redirect("profile")
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.title}' added successfully!")
            return redirect("book-list")
        else:
            messages.error(request, "Please correct the errors below.")
            print(form.errors)
            return render(request, 'add_book.html', {'form': form})
    return render(request, 'add_book.html', {'form': form})

def list_book(request):
    """
    List all books the server

    Args:
        request (_type_): _description_
    """
    search_query = request.GET.get("search", "").strip()
    
    if search_query:
        books = models.Books.objects.filter(author__icontains=search_query)| models.Books.objects.filter(title__icontains=search_query)
        books = books.distinct().order_by("title")
    else:
        books = models.Books.objects.all().order_by("title")
    
    paginator = Paginator(books, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, "book_list.html", context)


def book_management(request):
    pass

def borrow_management(request):
    pass