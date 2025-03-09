# Unit Tests for Book Model

import pytest
from django.contrib.auth.models import User
from library.models import Book


@pytest.mark.django_db
def test_create_book():
    user = User.objects.create_user(username="testuser", password="password")
    book = Book.objects.create(
        title="Test Book",
        author="Test Author",
        published_date="2024-01-01",
        added_by=user  # Fix: Set added_by field
    )
    assert book.title == "Test Book"
    assert book.is_borrowed is False  # Default value


@pytest.mark.django_db
def test_borrow_book():
    user = User.objects.create_user(username="testuser", password="password")
    book = Book.objects.create(
        title="Test Book",
        author="Test Author",
        added_by=user  # Fix: Set added_by field
    )
    
    book.is_borrowed = True
    book.borrowed_by = user
    book.save()
    
    assert book.is_borrowed is True
    assert book.borrowed_by == user


@pytest.mark.django_db
def test_book_creation():
    """Test book creation and __str__ method."""
    user = User.objects.create(username="testuser", email="test@example.com")
    book = Book.objects.create(
        title="Test Book", author="John Doe", added_by=user
    )
    
    assert book.title == "Test Book"
    assert str(book) == "Test Book"
    assert book.is_borrowed is False
    assert book.borrowed_by is None
    assert book.borrowed_at is None
