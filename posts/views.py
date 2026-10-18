from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.pagination import StandardPagination
from core.permissions import IsOwnerOrReadOnly
from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    Otomatik olarak şu endpoint'leri açar:
    - GET    /api/posts/          → liste
    - POST   /api/posts/          → oluştur
    - GET    /api/posts/{id}/     → detay
    - PUT    /api/posts/{id}/     → tam güncelle
    - PATCH  /api/posts/{id}/     → kısmi güncelle
    - DELETE /api/posts/{id}/     → sil (soft delete)
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        # Silinmiş postları gösterme + author'ı tek sorguda çek (N+1 önlemi)
        qs = (
            Post.objects
            .filter(is_deleted=False)
            .select_related('author')
        )

        # ?author=ahmet filtresi — bir kullanıcının postları
        username = self.request.query_params.get('author')
        if username:
            qs = qs.filter(author__username=username)

        return qs

    def perform_create(self, serializer):
        # Author istemciden DEĞİL, oturumdan gelir (güvenlik)
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        # SOFT DELETE — fiziksel silme yerine işaretle
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    # ----------------------------------------------------------------
    # Özel endpoint: GET /api/posts/my_posts/
    # Sadece kendi postlarını göster (feed için)
    # ----------------------------------------------------------------
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_posts(self, request):
        qs = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)