import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from posts.models import Post
from notifications.models import Notification

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
def test_list_notifications(auth_client, user):
    actor = User.objects.create_user(username='actor', password='password')
    post = Post.objects.create(author=user, content='Post')
    
    # Kullanıcıya bir bildirim oluştur
    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.Type.LIKE,
        post=post
    )
    
    url = reverse('notification-list')
    response = auth_client.get(url)
    
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['results'][0]['notification_type'] == 'like'

@pytest.mark.django_db
def test_mark_notification_as_read(auth_client, user):
    actor = User.objects.create_user(username='actor2', password='password')
    notification = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.Type.FOLLOW
    )
    
    url = reverse('notification-read', kwargs={'pk': notification.id})
    response = auth_client.patch(url)
    
    assert response.status_code == 200
    notification.refresh_from_db()
    assert notification.is_read is True

@pytest.mark.django_db
def test_mark_all_notifications_as_read(auth_client, user):
    actor = User.objects.create_user(username='actor3', password='password')
    Notification.objects.create(recipient=user, actor=actor, notification_type=Notification.Type.LIKE)
    Notification.objects.create(recipient=user, actor=actor, notification_type=Notification.Type.FOLLOW)
    
    url = reverse('notification-mark-all-read')
    response = auth_client.post(url)
    
    assert response.status_code == 200
    assert Notification.objects.filter(recipient=user, is_read=False).count() == 0