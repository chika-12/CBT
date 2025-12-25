from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . import models
from .serializer import BookForm, BookSuggestionForm
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import View
from django.db.models import Q



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

@login_required
def read_book(request, bookId):
    try:
        book = models.Books.objects.get(id=bookId)
                    
    except models.Books.DoesNotExist:
        messages.error(request, "Book not found")
        return redirect("book_list")
    
    # Get book content - assuming you have a content field or can read from file
    book_content = book.content if hasattr(book, 'content') else ""
    
    # If book content is stored in a file
    if not book_content:
        book_content = "Unable to load book content."
    
    # Split content into pages for better reading experience
    pages = []
    if book_content:
        # Split by paragraphs or fixed character length
        paragraphs = book_content.split('\n\n')
        current_page = []
        current_length = 0
        
        for paragraph in paragraphs:
            para_length = len(paragraph)
            if current_length + para_length > 2000:  # ~2000 chars per page
                pages.append('\n\n'.join(current_page))
                current_page = [paragraph]
                current_length = para_length
            else:
                current_page.append(paragraph)
                current_length += para_length
        
        if current_page:
            pages.append('\n\n'.join(current_page))
    
    context = {
        "book": book,
        "book_content": book_content,
        "pages": pages,
        "total_pages": len(pages) if pages else 1,
        "current_page": 1,
    }
    return render(request, "book_page.html", context)
    

@login_required  # Optional: if you want only logged-in users to submit
def suggest_book(request):
    if request.method == 'POST':
        # Get form data from request
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn', '')
        publication_year = request.POST.get('publication_year')
        genre = request.POST.get('genre', '')
        reason = request.POST.get('reason')
        source = request.POST.get('source', '')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not title or not author or not reason:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'suggest_book.html')
        
        try:
            # Create and save BookSuggestion object
            suggestion = models.BookSuggestion.objects.create(
                user=request.user if request.user.is_authenticated else None,
                title=title,
                author=author,
                isbn=isbn,
                publication_year=publication_year if publication_year else None,
                genre=genre,
                reason=reason,
                source=source,
                notes=notes,
            )
            
            # Success message
            messages.success(
                request, 
                f"Thank you! Your suggestion for '{title}' has been submitted successfully."
            )
            return redirect('suggest_book')  # Redirect to clear form
            
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'suggest_book.html')
    
    return render(request, 'suggest_book.html')



@login_required
def admin_view_suggested_books(request):
    """
    Admin view to see and manage all book suggestions
    """
    profile = get_object_or_404(Profile, user=request.user)
    if profile.role != "admin":
        messages.error(request, "Unauthorized action")
        return redirect("/")

    # Base queryset
    suggestions = (
        models.BookSuggestion.objects
        .select_related("user")
        .order_by("-suggested_at")
    )

    # --------------------
    # Filters
    # --------------------
    reviewed_filter = request.GET.get("reviewed", "")
    genre_filter = request.GET.get("genre", "")
    source_filter = request.GET.get("source", "")
    user_type_filter = request.GET.get("user_type", "")

    if reviewed_filter == "reviewed":
        suggestions = suggestions.filter(reviewed=True)
    elif reviewed_filter == "pending":
        suggestions = suggestions.filter(reviewed=False)

    if genre_filter:
        suggestions = suggestions.filter(genre=genre_filter)

    if source_filter:
        suggestions = suggestions.filter(source=source_filter)

    if user_type_filter == "registered":
        suggestions = suggestions.filter(user__isnull=False)
    elif user_type_filter == "anonymous":
        suggestions = suggestions.filter(user__isnull=True)

    # --------------------
    # Search
    # --------------------
    search_query = request.GET.get("search", "")
    if search_query:
        suggestions = suggestions.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # --------------------
    # Sorting
    # --------------------
    sort_by = request.GET.get("sort", "-suggested_at")
    allowed_sort_fields = [
        "title",
        "author",
        "genre",
        "suggested_at",
        "reviewed",
    ]

    if sort_by.lstrip("-") in allowed_sort_fields:
        suggestions = suggestions.order_by(sort_by)

    # --------------------
    # Pagination
    # --------------------
    paginator = Paginator(suggestions, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --------------------
    # Statistics
    # --------------------
    stats = {
        "total": models.BookSuggestion.objects.count(),
        "pending": models.BookSuggestion.objects.filter(reviewed=False).count(),
        "reviewed": models.BookSuggestion.objects.filter(reviewed=True).count(),
        "anonymous": models.BookSuggestion.objects.filter(user__isnull=True).count(),
        "registered": models.BookSuggestion.objects.filter(user__isnull=False).count(),
    }

    context = {
        "suggestions": page_obj,
        "page_obj": page_obj,
        "stats": stats,
        "reviewed_filter": reviewed_filter,
        "genre_filter": genre_filter,
        "source_filter": source_filter,
        "user_type_filter": user_type_filter,
        "search_query": search_query,
        "sort_by": sort_by,
        "genre_choices": models.BookSuggestion.GENRE_CHOICES,
        "source_choices": models.BookSuggestion.SOURCE_CHOICES,
    }

    return render(request, "view_suggested_books.html", context)


@login_required
def update_suggestion_status(request, suggestion_id):
    """
    Admin view to update suggestion status
    """
    if Profile.objects.get(user=request.user).role != "admin":
        messages.error(request, "Unauthorized Action")
        return redirect("progfile")
    suggestion = get_object_or_404(models.BookSuggestion, id=suggestion_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        review_notes = request.POST.get('review_notes', '')
        
        if new_status in dict(models.BookSuggestion.STATUS_CHOICES).keys():
            suggestion.status = new_status
            suggestion.review_notes = review_notes
            suggestion.reviewed_by = request.user
            suggestion.review_date = timezone.now()
            suggestion.save()
            
            messages.success(request, f'Suggestion status updated to {suggestion.get_status_display()}')
            
        
        return redirect('view_suggested_books')
    
    return redirect('view_suggested_books')


def book_management(request):
    pass

def borrow_management(request):
    pass