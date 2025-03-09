# Unit Tests for Authentication

import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_sso_login_redirect(client):
    """Test if the login redirects to Auth0 authentication."""
    response = client.get(reverse("login"))
    assert response.status_code == 302
    assert "auth0" in response.url  # Ensure it redirects to Auth0

@pytest.mark.django_db
def test_sso_logout_clears_session(client):
    """Test if the logout clears session and redirects."""
    session = client.session
    session["user"] = {"name": "Test User", "email": "test@example.com"}
    session.save()

    response = client.get(reverse("logout"))
    assert response.status_code == 302  # Redirect after logout
    assert "user" not in client.session  # Ensure session is cleared
