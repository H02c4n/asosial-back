from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification
from .serializers import NotificationSerializer


def notify(*, recipient, actor, notification_type, post=None, comment=None):
    """
    Bildirim oluşturur (DB) ve alıcıya WebSocket üzerinden iter.

    - recipient: bildirimi ALAN kullanıcı
    - actor: eylemi YAPAN kullanıcı
    - notification_type: Notification.Type.* (FOLLOW, COMMENT, LIKE)
    - post / comment: opsiyonel referanslar

    Kendi kendine bildirim yapılmaz (recipient == actor).
    Aynı anda 2 bildirim oluşursa (self-comment gibi) DB'ye de yazılmaz.
    """
    if recipient.id == actor.id:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        post=post,
        comment=comment,
    )

    # WebSocket'e gönder — alıcının grubuna
    channel_layer = get_channel_layer()
    data = NotificationSerializer(notification).data

    async_to_sync(channel_layer.group_send)(
        f'user_{recipient.id}',
        {
            'type': 'notification.message',   # → consumer.notification_message()
            'data': data,
        },
    )

    return notification