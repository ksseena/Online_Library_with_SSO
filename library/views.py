
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from django.contrib.auth import logout
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.contrib.auth.models import User
from django.contrib.auth import login
from functools import wraps
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now


# Initialize OAuth for authentication with Auth0
oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

# Home page view
def index(request):

    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

# Callback view for handling OAuth response
def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        return redirect("login")
    
    username = user_info.get("given_name", "") 
    email = user_info.get("email", "")
    user, created = User.objects.get_or_create(
        username=username, 
        defaults={"email": email, "first_name": user_info.get("name", "")},
    )
    login(request, user)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("book_list")))

# Login view that redirects to Auth0 login
def login_view(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

# Logout view that clears the session and logs out from Auth0
def logout_user(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

# Decorator for requiring authentication
def auth0_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user"):
            return redirect("login")  # Redirect to Auth0 login if user is not authenticated
        return view_func(request, *args, **kwargs)
    return wrapper

# Book list view with search functionality
@auth0_login_required
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return render(request, "library/book_list.html", {"books": books, "query": query})


# View to add a new book
@auth0_login_required
def book_new(request):
    if request.method == "POST":
        title = request.POST["title"]
        author = request.POST["author"]
        published_date = request.POST.get("published_date")  # Optional
        
        user_info = request.session.get("user", {}).get("userinfo", {})
        auth0_user_id = user_info.get("sub")  # Unique Auth0 user ID
        user_email = user_info.get("email")  # Email (can be used instead)

        user, _ = User.objects.get_or_create(username=user_email, defaults={"email": user_email})

        Book.objects.create(
            title=title,
            author=author,
            published_date=published_date if published_date else None,
            added_by=user  # Django User instance
        )
        return redirect("book_list")
    return render(request, "library/book_add.html")


# View to edit an existing book
@auth0_login_required
def book_edit(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.published_date = request.POST.get("published_date") or None  # Handle empty date
        book.is_borrowed = "is_borrowed" in request.POST  # Checkbox handling
        book.save()
        return redirect("book_list")

    return render(request, "library/book_edit.html", {"book": book})

# View to delete a book
@auth0_login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("book_list")

# View to borrow a book
@auth0_login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.is_borrowed:
        messages.error(request, "This book is already borrowed.")
        return redirect("book_list")

    book.is_borrowed = True
    book.borrowed_by = request.user
    book.borrowed_at = now()
    book.save()

    # Send email notification
    send_mail(
        "Book Borrowed",
        f"You have borrowed '{book.title}' by {book.author}.",
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
    )

    messages.success(request, "Book borrowed successfully!")
    return redirect("book_list")

# View to return a borrowed book
@auth0_login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, borrowed_by=request.user)

    book.is_borrowed = False
    book.borrowed_by = None
    book.borrowed_at = None
    book.save()

    # Send email notification
    send_mail(
        "Book Returned",
        f"You have returned '{book.title}' by {book.author}.",
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
    )

    messages.success(request, "Book returned successfully!")
    return redirect("book_list")

