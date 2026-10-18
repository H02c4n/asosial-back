from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    # display name: "follow" → "Takip" gibi insan-okur metin
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'notification_type', 'notification_type_display',
            'post', 'comment', 'is_read', 'created_at',
        ]
        read_only_fields = fields  # bildirimler sadece backend tarafından oluşturulur