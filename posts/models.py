from django.conf import settings
from django.db import models

from core.models import BaseModel


class Post(BaseModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # 'users.User' — string olduğu için döngüsel import yok
        on_delete=models.CASCADE,       # kullanıcı silinirse postları da gider
        related_name='posts',           # user.posts.all()
    )
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta(BaseModel.Meta):
        # BaseModel.Meta'daki ordering'i miras alır: -created_at
        indexes = [
            models.Index(fields=['-created_at']),       # feed sıralaması hızlı olsun
            models.Index(fields=['author', '-created_at']),  # "kullanıcının postları" hızlı olsun
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"



class Like(BaseModel):
    """
    Kullanıcı bir postu beğenebilir. Aynı kullanıcı aynı postu
    sadece bir kez beğenebilir (unique_together).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )

    class Meta(BaseModel.Meta):
        unique_together = ('user', 'post')   # bir kullanıcı bir postu bir kez beğenir
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} ♥ {self.post_id}"