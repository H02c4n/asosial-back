import json

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):
    help = 'Yorum eventlerini sayarak analytics tutar (mock)'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_COMMENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,   # ← DEĞİŞTİ
            group_id='analytics-service',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        )
        self.stdout.write(self.style.SUCCESS('[Analytics Consumer] Dinleniyor...'))

        counter = 0
        for msg in consumer:
            data = msg.value
            counter += 1
            self.stdout.write(
                f"[Analytics] Toplam yorum: {counter} | post_id={data['post_id']} user=@{data['actor_username']}"
            )