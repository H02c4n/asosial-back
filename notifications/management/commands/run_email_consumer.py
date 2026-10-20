import json

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):
    help = 'Yorum eventlerinde post sahibine mock email gönderir'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_COMMENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,   # ← DEĞİŞTİ
            group_id='email-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        self.stdout.write(self.style.SUCCESS('[Email Consumer] Dinleniyor...'))

        for msg in consumer:
            data = msg.value
            self.stdout.write(
                f"[Email] To user_{data['post_author_id']}: "
                f"@{data['actor_username']} yorum yaptı → {data['content'][:40]}"
            )