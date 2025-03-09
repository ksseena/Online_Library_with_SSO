# # Unit Tests for Book Views
# Tests implemented:


import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from library.models import Book

#  List books
@pytest.mark.django_db
def test_book_list_view(client):
    session = client.session
    session["user"] = {"userinfo": {"email": "testuser@example.com", "sub": "auth0|testuser"}}
    session.save()

    response = client.get(reverse("book_list"))

    assert response.status_code == 200  # Should now load successfully


#  Create a book
@pytest.mark.django_db
def test_book_creation(client):
    """Test that a logged-in user can create a book."""
    # user = User.objects.create_user(username="testuser", password="password")
    user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")

    client.force_login(user)

    # Simulate Auth0 session data
    session = client.session
    session["user"] = {
        "userinfo": {
            "sub": "auth0|12345",
            "email": "testuser@example.com"
        }
    }
    session.save()

    response = client.post(reverse("book_new"), {
        "title": "New Book",
        "author": "John Doe",
        "published_date": "2025-03-10"
    })

    assert response.status_code == 302  # Check for redirect after creation
    assert response.url == reverse("book_list")  # Ensure correct redirection

    # Verify book was created
    assert Book.objects.count() == 1
    book = Book.objects.first()
    assert book.title == "New Book"
    assert book.author == "John Doe"
    assert book.added_by == user  # Ensure correct ownership


#  Edit a book Test Case
@pytest.mark.django_db
def test_book_edit(client):
    """Test that a logged-in user can edit a book."""
    user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")
    client.force_login(user)

    # Simulate Auth0 session data
    session = client.session
    session["user"] = {
        "userinfo": {
            "sub": "auth0|12345",
            "email": user.email
        }
    }
    session.save()

    # Create a book
    book = Book.objects.create(title="Old Title", author="John Doe", added_by=user)

    # Edit the book
    response = client.post(reverse("book_edit", args=[book.id]), {
        "title": "Updated Title",
        "author": "Updated Author",
        "published_date": "2025-04-01"
    }, follow=True)

    # Refresh from DB
    book.refresh_from_db()

    # Assertions
    assert response.status_code == 200  # Ensure successful response
    assert book.title == "Updated Title"  # Check if the title is updated
    assert book.author == "Updated Author"  # Check if the author is updated


#  Delete a book
@pytest.mark.django_db
def test_book_delete(client):
    """Test that a book can be deleted."""
    user = User.objects.create_user(username="testuser@example.com", password="password")
    client.force_login(user)

    # Simulate Auth0 session data
    session = client.session
    session["user"] = {
        "userinfo": {
            "sub": "auth0|12345",
            "email": user.email
        }
    }
    session.save()

    book = Book.objects.create(title="Book to Delete", author="John", added_by=user)

    # Ensure book exists before deletion
    assert Book.objects.filter(id=book.id).exists()

    response = client.post(reverse("book_delete", args=[book.id]))

    assert response.status_code == 302  # Ensure redirect
    assert response.url == reverse("book_list")  # Ensure correct redirection

    # Ensure book is deleted
    assert not Book.objects.filter(id=book.id).exists()

#  Borrow a book Test Case
@pytest.mark.django_db
def test_borrow_book_view(client):
    # Create a user matching Auth0 session details
    user = User.objects.create_user(username="auth0|testuser", email="testuser@example.com", password="password")

    # Simulate Auth0 session
    session = client.session
    session["user"] = {"userinfo": {"email": user.email, "sub": user.username}}  # Match Auth0 ID
    session.save()

    # Authenticate user manually in Django
    client.force_login(user)  

    # Create a book
    admin_user = User.objects.create_user(username="admin", password="password")
    book = Book.objects.create(
        title="Test Book",
        author="Test Author",
        added_by=admin_user
    )

    # Borrow the book
    response = client.post(reverse("borrow_book", args=[book.id]), follow=True)

    # Refresh book instance from the database
    book.refresh_from_db()

    # Assertions
    assert response.status_code == 200  # Successful request
    assert book.is_borrowed is True  # Book should now be marked as borrowed
    assert book.borrowed_by == user  # Check correct user is set


#  Return a book test case
@pytest.mark.django_db
def test_return_book(client):
    """Test that a borrowed book can be returned."""
    user = User.objects.create_user(username="testuser@example.com", email="testuser@example.com", password="password")
    client.force_login(user)

    # Simulate Auth0 session
    session = client.session
    session["user"] = {
        "userinfo": {
            "sub": "auth0|12345",
            "email": user.email
        }
    }
    session.save()

    # Create a book and mark it as borrowed
    admin_user = User.objects.create_user(username="admin", password="password")
    book = Book.objects.create(
        title="Borrowed Book",
        author="Author Name",
        added_by=admin_user,
        is_borrowed=True,
        borrowed_by=user
    )

    # Return the book
    response = client.post(reverse("return_book", args=[book.id]), follow=True)

    # Refresh book instance from the database
    book.refresh_from_db()

    # Assertions
    assert response.status_code == 200  # Ensure successful response
    assert book.is_borrowed is False  # Ensure book is no longer borrowed
    assert book.borrowed_by is None  # Ensure borrowed_by field is cleared
