import json
import logging

from django.conf import settings
from kafka import KafkaProducer

logger = logging.getLogger(__name__)

_producer = None


def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3,
            acks='all',
        )
    return _producer


def publish_comment_created(*, comment_id, post_id, post_author_id, actor_id, actor_username, content):
    """Yorum oluşturulduğunda Kafka'ya event gönderir."""
    producer = get_producer()
    payload = {
        'event': 'comment.created',
        'comment_id': comment_id,
        'post_id': post_id,
        'post_author_id': post_author_id,
        'actor_id': actor_id,
        'actor_username': actor_username,
        'content': content,
    }
    future = producer.send(settings.KAFKA_TOPIC_COMMENTS, value=payload)
    try:
        future.get(timeout=5)  # senkron onay — hata varsa yakala
        logger.info("[Kafka] comment.created gönderildi: %s", comment_id)
    except Exception as e:
        logger.error("[Kafka] Gönderim hatası: %s", e)