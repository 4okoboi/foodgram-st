import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='securepassword123',
        first_name='Test',
        last_name='User'
    )
    assert user.email == 'test@example.com'
    assert user.username == 'testuser'
    assert user.check_password('securepassword123') is True
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
