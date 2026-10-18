from rest_framework import viewsets, permissions

from core.pagination import StandardPagination
from core.permissions import IsOwnerOrReadOnly
from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = (
            Comment.objects
            .filter(is_deleted=False)
            .select_related('author', 'post')
        )

        # ?post=5 filtresi — bir postun yorumları
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)

        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])