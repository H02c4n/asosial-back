import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer

from notifications.models import Notification
from notifications.services import notify


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Kafka comment.created eventlerini dinleyip bildirim oluşturur'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_COMMENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,   # ← DEĞİŞTİ
            group_id='notification-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
        )
        self.stdout.write(self.style.SUCCESS('[Notification Consumer] Dinleniyor...'))

        for msg in consumer:
            data = msg.value
            try:
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
                self.stdout.write(
                    f"[Notification] Bildirim oluşturuldu: comment_id={data['comment_id']}"
                )
            except Exception as e:
                logger.error(f"[Notification Consumer] Hata: {e}", exc_info=True)