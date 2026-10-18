from django.conf import settings
from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    """
    Bir kullanıcıya yönelik bildirim.
    Örn: "Ahmet senin postunu beğendi", "Mehmet seni takip etti"
    """

    class Type(models.TextChoices):
        FOLLOW = 'follow', 'Takip'
        LIKE = 'like', 'Beğeni'
        COMMENT = 'comment', 'Yorum'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',       # user.notifications.all()
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,           # eylemi yapan
        on_delete=models.CASCADE,
        related_name='sent_notifications',
    )
    notification_type = models.CharField(max_length=20, choices=Type.choices)

    # Hedef nesne — hangisi uygunsa dolu olur (nullable)
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        'comments.Comment', on_delete=models.CASCADE, null=True, blank=True
    )

    is_read = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),  # "okunmamışlarım" hızlı olsun
        ]

    def __str__(self):
        return f"{self.actor} → {self.recipient} ({self.notification_type})"