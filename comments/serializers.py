from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
        # 'post' yazılabilir — istemci yorum yaparken post id'sini gönderir

    def get_replies(self, obj):
        # sadece silinmemiş yanitlari getir
        replies = obj.replies.filter(is_deleted=False).order_by('created_at')
        return CommentSerializer(replies, many=True).data