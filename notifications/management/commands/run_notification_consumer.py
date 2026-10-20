import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer

from notifications.models import Notification
from notifications.services import notify


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Kafka eventlerini dinleyip bildirim oluşturur'

    def handle(self, *args, **options):
        # İKİ TOPIC birden dinleniyor
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_COMMENTS,
            settings.KAFKA_TOPIC_LIKES,     # ← EKLE
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id='notification-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
        )
        self.stdout.write(self.style.SUCCESS('[Notification Consumer] Dinleniyor...'))

        for msg in consumer:
            data = msg.value
            event = data.get('event')

            try:
                if event == 'comment.created':
                    self._handle_comment(data)
                elif event == 'like.created':
                    self._handle_like(data)
            except Exception as e:
                logger.error(f"[Notification Consumer] Hata: {e}", exc_info=True)

    def _handle_comment(self, data):
        from django.contrib.auth import get_user_model
        from posts.models import Post
        from comments.models import Comment

        User = get_user_model()
        recipient = User.objects.get(id=data['post_author_id'])
        actor = User.objects.get(id=data['actor_id'])
        post = Post.objects.get(id=data['post_id'])
        comment = Comment.objects.get(id=data['comment_id'])

        notify(
            recipient=recipient,
            actor=actor,
            notification_type=Notification.Type.COMMENT,
            post=post,
            comment=comment,
        )
        self.stdout.write(f"[Notification] Yorum bildirimi: comment_id={data['comment_id']}")

    def _handle_like(self, data):
        from django.contrib.auth import get_user_model
        from posts.models import Post

        User = get_user_model()
        recipient = User.objects.get(id=data['post_author_id'])
        actor = User.objects.get(id=data['actor_id'])
        post = Post.objects.get(id=data['post_id'])

        notify(
            recipient=recipient,
            actor=actor,
            notification_type=Notification.Type.LIKE,
            post=post,
        )
        self.stdout.write(f"[Notification] Beğeni bildirimi: post_id={data['post_id']}")