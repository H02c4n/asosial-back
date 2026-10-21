import json

from django.conf import settings
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer


class Command(BaseCommand):
    help = 'Yorum eventlerini sayarak analytics tutar (mock)'

    def handle(self, *args, **options):
        kafka_config = {
            'bootstrap_servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group_id': 'analytics-service',
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
        self.stdout.write(self.style.SUCCESS('[Analytics Consumer] Dinleniyor...'))

        counter = 0
        for msg in consumer:
            data = msg.value
            counter += 1
            self.stdout.write(
                f"[Analytics] Toplam yorum: {counter} | post_id={data['post_id']} user=@{data['actor_username']}"
            )