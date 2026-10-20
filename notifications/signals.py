from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment
from .kafka import publish_comment_created


@receiver(post_save, sender=Comment)
def publish_comment_event(sender, instance: Comment, created, **kwargs):
    """Yeni yorum → Kafka'ya comment.created event'i gönder."""
    if not created:
        return

    # Kendi postuna kendi yorumu → event gönderme (gereksiz)
    if instance.post.author_id == instance.author_id:
        return

    publish_comment_created(
        comment_id=instance.id,
        post_id=instance.post_id,
        post_author_id=instance.post.author_id,
        actor_id=instance.author_id,
        actor_username=instance.author.username,
        content=instance.content[:200],  # büyük payload göndermemek için kırp
    )



# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from comments.models import Comment
# from .models import Notification
# from .services import notify


# @receiver(post_save, sender=Comment)
# def notify_post_author_on_comment(sender, instance: Comment, created, **kwargs):
#     """Yeni bir yorum oluşturulduğunda post sahibine bildirim gönder."""
#     if not created:
#         return  # güncellemede değil, sadece oluşturmada

#     # Kendi postuna kendi yorumu → bildirim yok
#     if instance.post.author_id == instance.author_id:
#         return

#     notify(
#         recipient=instance.post.author,
#         actor=instance.author,
#         notification_type=Notification.Type.COMMENT,
#         post=instance.post,
#         comment=instance,
#     )