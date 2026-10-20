import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from posts.models import Post
from comments.models import Comment
from unittest.mock import patch

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='commenter', password='password123')

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
@patch('notifications.signals.publish_comment_created') # Kafka'yı mock'la
def test_create_comment(mock_kafka, auth_client, user):
    other_user = User.objects.create_user(username='author', password='password')
    post = Post.objects.create(author=other_user, content='Test Post')
    
    url = reverse('comment-list')
    payload = {'post': post.id, 'content': 'Harika bir post!'}
    response = auth_client.post(url, payload)
    
    assert response.status_code == 201
    assert Comment.objects.count() == 1
    assert mock_kafka.called # Kafka event'i tetiklendi mi?

@pytest.mark.django_db
@patch('notifications.signals.publish_comment_created')
def test_create_nested_comment(mock_kafka, auth_client, user):
    other_user = User.objects.create_user(username='author', password='password')
    post = Post.objects.create(author=other_user, content='Test Post')
    
    # Ana yorum
    parent_comment = Comment.objects.create(post=post, author=other_user, content='Ana yorum')
    
    url = reverse('comment-list')
    payload = {'post': post.id, 'content': 'Buna yanıt!', 'parent': parent_comment.id}
    response = auth_client.post(url, payload)
    
    assert response.status_code == 201
    new_comment = Comment.objects.last()
    assert new_comment.parent == parent_comment
    assert new_comment.author == user

@pytest.mark.django_db
def test_soft_delete_comment(auth_client, user):
    post = Post.objects.create(author=user, content='Post')
    comment = Comment.objects.create(post=post, author=user, content='Silinecek yorum')
    
    url = reverse('comment-detail', kwargs={'pk': comment.id})
    response = auth_client.delete(url)
    
    assert response.status_code == 204
    comment.refresh_from_db()
    assert comment.is_deleted is True # Veritabanında var ama silinmiş işaretli