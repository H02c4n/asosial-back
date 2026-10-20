from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.pagination import StandardPagination
from core.permissions import IsOwnerOrReadOnly
from .models import Post
from posts.models import Post, Like
from notifications.kafka import publish_like_created
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """POST /api/posts/{id}/like/ — beğen"""
        post = self.get_object()

        if post.author_id == request.user.id:
            return Response(
                {'detail': 'Kendi postunuzu beğenemezsiniz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'is_deleted': False},
        )

        if not created and like.is_deleted:
            # Daha önce beğenmiş, silmiş → tekrar beğen
            like.is_deleted = False
            like.save(update_fields=['is_deleted', 'updated_at'])
        elif not created and not like.is_deleted:
            # Zaten beğenilmiş
            return Response(
                {'detail': 'Bu postu zaten beğendiniz.'},
                status=status.HTTP_200_OK,
            )

        # Kafka'ya event gönder
        publish_like_created(
            like_id=like.id,
            post_id=post.id,
            post_author_id=post.author_id,
            actor_id=request.user.id,
            actor_username=request.user.username,
        )

        return Response({'detail': 'Beğenildi.', 'is_liked': True})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        """POST /api/posts/{id}/unlike/ — beğeniyi geri al"""
        post = self.get_object()

        updated = Like.objects.filter(
            user=request.user, post=post, is_deleted=False
        ).update(is_deleted=True)

        if not updated:
            return Response(
                {'detail': 'Bu postu zaten beğenmemişsiniz.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'detail': 'Beğeni geri alındı.', 'is_liked': False})

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