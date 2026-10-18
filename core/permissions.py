from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - Okuma (GET, HEAD, OPTIONS): herkese açık
    - Yazma/Silme (POST, PUT, PATCH, DELETE): sadece nesne sahibine

    'author' veya 'user' alanı olan modellerle çalışır.
    """
    message = 'Bu işlem için bu nesnenin sahibi olmalısınız.'

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True

        # Sahibi bul: author veya user alanı
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user