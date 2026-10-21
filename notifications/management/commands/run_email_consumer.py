import json

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):
    help = 'Yorum eventlerinde post sahibine mock email gönderir'

    def handle(self, *args, **options):
        kafka_config = {
            'bootstrap_servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group_id': 'email-service',
            'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
        }

        if settings.KAFKA_USERNAME and settings.KAFKA_PASSWORD:
            kafka_config.update({
                'security_protocol': 'SASL_SSL',
                'sasl_mechanism': 'SCRAM-SHA-256',
                'sasl_plain_username': settings.KAFKA_USERNAME,
                'sasl_plain_password': settings.KAFKA_PASSWORD,
                'ssl_cafile': settings.KAFKA_CA_CERT,
            })

        consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_COMMENTS,
            **kafka_config
        )
        self.stdout.write(self.style.SUCCESS('[Email Consumer] Dinleniyor...'))

        for msg in consumer:
            data = msg.value
            self.stdout.write(
                f"[Email] To user_{data['post_author_id']}: "
                f"@{data['actor_username']} yorum yaptı → {data['content'][:40]}"
            )