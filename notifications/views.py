from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.pagination import StandardPagination
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/notifications/                  → kendi bildirimlerim
    GET  /api/notifications/{id}/             → detay (opsiyonel)
    PATCH /api/notifications/{id}/read/       → okundu işaretle
    POST /api/notifications/mark_all_read/    → hepsini okundu işaretle
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Notification.objects
            .filter(recipient=self.request.user, is_deleted=False)
            .select_related('actor', 'post', 'comment')
            .order_by('-created_at')
        )

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read', 'updated_at'])
        return Response({'detail': 'ok'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        count = (
            self.get_queryset()
            .filter(is_read=False)
            .update(is_read=True)
        )
        return Response({'marked': count})