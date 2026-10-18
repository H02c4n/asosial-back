from django.conf import settings
from django.db import models

from core.models import BaseModel


class Comment(BaseModel):
    post = models.ForeignKey(
        'posts.Post',                # string referans — posts app'ini import etmiyoruz
        on_delete=models.CASCADE,
        related_name='comments',     # post.comments.all()
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField(max_length=1000)

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=['post', 'created_at']),  # postun yorumlarını sırayla çekmek için
        ]

    def __str__(self):
        return f"{self.author.username} → {self.post_id}: {self.content[:30]}"