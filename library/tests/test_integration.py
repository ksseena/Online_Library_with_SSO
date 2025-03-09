import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from library.models import Book
import pytest
from django.contrib.auth import get_user_model
from library.models import Book

User = get_user_model()

# =======================================
# Integration Tests for Views
# =======================================

@pytest.fixture
def auth_client(client, django_db_blocker):
    """Fixture to create a user and log them in with an Auth0 session."""
    with django_db_blocker.unblock():
        user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")
        client.force_login(user)

        session = client.session
        session["user"] = {
            "userinfo": {
                "sub": "auth0|12345",
                "email": user.email
            }
        }
        session.save()
    return client, user

@pytest.mark.django_db
def test_book_list_view(auth_client):
    """Ensure books can be listed."""
    client, user = auth_client

    # Create sample books
    Book.objects.create(title="Book 1", author="Author A", added_by=user)
    Book.objects.create(title="Book 2", author="Author B", added_by=user)

    response = client.get(reverse("book_list"))

    assert response.status_code == 200
    assert b"Book 1" in response.content
    assert b"Book 2" in response.content

@pytest.mark.django_db
def test_book_creation(auth_client):
    """Ensure a user can create a book."""
    client, user = auth_client

    response = client.post(reverse("book_new"), {
        "title": "New Book",
        "author": "John Doe",
        "published_date": "2025-03-10"
    }, follow=True)

    assert response.status_code == 200
    assert Book.objects.count() == 1
    book = Book.objects.first()
    assert book.title == "New Book"
    assert book.author == "John Doe"
    assert book.added_by == user


@pytest.mark.django_db
def test_book_edit(auth_client):
    """Ensure a user can edit a book."""
    client, user = auth_client

    book = Book.objects.create(title="Old Title", author="Author", added_by=user)

    response = client.post(reverse("book_edit", args=[book.id]), {
        "title": "Updated Title",
        "author": "Updated Author",
        "published_date": "2025-04-01"
    }, follow=True)

    book.refresh_from_db()
    assert response.status_code == 200
    assert book.title == "Updated Title"
    assert book.author == "Updated Author"


@pytest.mark.django_db
def test_book_delete(auth_client):
    """Ensure a user can delete a book."""
    client, user = auth_client

    book = Book.objects.create(title="To Be Deleted", author="John Doe", added_by=user)

    response = client.post(reverse("book_delete", args=[book.id]), follow=True)

    assert response.status_code == 200
    assert not Book.objects.filter(id=book.id).exists()


@pytest.mark.django_db
def test_borrow_book(auth_client):
    """Ensure a user can borrow a book."""
    client, user = auth_client

    book = Book.objects.create(title="Borrowable Book", author="Test Author", added_by=user)

    response = client.post(reverse("borrow_book", args=[book.id]), follow=True)

    book.refresh_from_db()
    assert response.status_code == 200
    assert book.is_borrowed is True
    assert book.borrowed_by == user

@pytest.mark.django_db
def test_return_book(auth_client):
    """Ensure a borrowed book can be returned."""
    client, user = auth_client

    book = Book.objects.create(title="Borrowed Book", author="Author", added_by=user, is_borrowed=True, borrowed_by=user)

    response = client.post(reverse("return_book", args=[book.id]), follow=True)

    book.refresh_from_db()
    assert response.status_code == 200
    assert book.is_borrowed is False
    assert book.borrowed_by is None


# =======================================
# Integration Tests for Models
# =======================================
    
@pytest.mark.django_db
def test_book_str():
    """Ensure the book string representation works correctly."""
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password")

    book = Book.objects.create(title="Test Book", author="Author Name", added_by=user)

    assert str(book) == "Test Book by Author Name"

@pytest.mark.django_db
def test_book_borrowing():
    """Ensure borrowing a book updates the correct fields."""
    user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")
    added_by = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="password")

    book = Book.objects.create(title="Book to Borrow", author="Author Name", added_by=added_by)

    book.borrowed_by = user
    book.is_borrowed = True
    book.save()

    book.refresh_from_db()
    assert book.is_borrowed is True
    assert book.borrowed_by == user


@pytest.mark.django_db
def test_book_returning():
    """Ensure returning a book resets fields."""
    user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")
    added_by = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="password")

    book = Book.objects.create(title="Borrowed Book", author="Author Name", added_by=added_by, borrowed_by=user, is_borrowed=True)

    book.borrowed_by = None
    book.is_borrowed = False
    book.save()

    book.refresh_from_db()
    assert book.is_borrowed is False
    assert book.borrowed_by is None


