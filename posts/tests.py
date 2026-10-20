import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from posts.models import Post, Like
from unittest.mock import patch

User = get_user_model()

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

@pytest.mark.django_db
def test_create_post(auth_client, user):
    url = reverse('post-list')
    response = auth_client.post(url, {'content': 'Test post içeriği'})
    assert response.status_code == 201
    assert Post.objects.count() == 1
    assert Post.objects.first().author == user

# Kafka fonksiyonunu mock'layarak dış servis bağımlılığını kaldırıyoruz
@patch('posts.views.publish_like_created')
@pytest.mark.django_db
def test_like_post(mock_kafka, auth_client, user):
    # Başka bir kullanıcının postunu oluştur
    other_user = User.objects.create_user(username='user2', password='password')
    post = Post.objects.create(author=other_user, content='Beğenilecek post')
    
    url = reverse('post-like', kwargs={'pk': post.id})
    response = auth_client.post(url)
    
    assert response.status_code == 200
    assert Like.objects.filter(user=user, post=post, is_deleted=False).exists()
    # Kafka fonksiyonunun çağrıldığını doğrula
    mock_kafka.assert_called_once()

@pytest.mark.django_db
def test_like_own_post_fails(auth_client, user):
    post = Post.objects.create(author=user, content='Kendi postum')
    url = reverse('post-like', kwargs={'pk': post.id})
    response = auth_client.post(url)
    assert response.status_code == 400 # Bad Request