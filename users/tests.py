import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    url = reverse('register')
    payload = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'StrongPassword123!',
        'password2': 'StrongPassword123!'
    }
    response = client.post(url, payload)
    assert response.status_code == 201
    assert 'access' in response.data
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_user_login():
    User.objects.create_user(username='testuser', password='StrongPassword123!')
    client = APIClient()
    url = reverse('login')
    response = client.post(url, {'username': 'testuser', 'password': 'StrongPassword123!'})
    assert response.status_code == 200
    assert 'access' in response.data

# --- EKSİK OLAN FIXTURE'LAR BURAYA EKLENDİ ---
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='user1', password='password123')

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
# ---------------------------------------------

@pytest.mark.django_db
@patch('users.views.notify')
def test_follow_user(mock_notify, auth_client, user):
    target_user = User.objects.create_user(username='target', password='password')
    url = reverse('user-follow', kwargs={'username': target_user.username})
    
    response = auth_client.post(url)
    
    assert response.status_code == 200
    assert user.following.filter(id=target_user.id).exists()
    assert mock_notify.called

@pytest.mark.django_db
def test_unfollow_user(auth_client, user):
    target_user = User.objects.create_user(username='target2', password='password')
    user.following.add(target_user)
    
    url = reverse('user-unfollow', kwargs={'username': target_user.username})
    response = auth_client.post(url)
    
    assert response.status_code == 200
    assert not user.following.filter(id=target_user.id).exists()

@pytest.mark.django_db
def test_update_profile(auth_client, user):
    url = reverse('me')
    payload = {'first_name': 'Yeni', 'last_name': 'İsim', 'bio': 'Merhaba dünya!'}
    
    response = auth_client.patch(url, payload)
    
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == 'Yeni'
    assert user.bio == 'Merhaba dünya!'