from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    AbstractUser'dan türeyen custom User.
    AbstractUser zaten: username, email, password, first_name, last_name,
    is_active, date_joined alanlarını getirir.
    """
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Takip sistemi: user X, user Y'yi takip ediyor
    # symmetrical=False → A, B'yi takip ettiğinde B otomatik A'yı takip etmez
    # related_name='followers' → user.followers.all() ile "beni takip edenler"
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
    )

    def __str__(self):
        return self.username