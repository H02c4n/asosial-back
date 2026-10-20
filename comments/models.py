from django.conf import settings
from django.db import models

from core.models import BaseModel


class Comment(BaseModel):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    
    # YENİ: Kendi kendine referans veren parent alanı
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
        # Varsayılan sıralama: en eskiler önce (yorumlar için daha mantıklı)
        ordering = ['created_at']