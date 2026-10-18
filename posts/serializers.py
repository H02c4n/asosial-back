from rest_framework import serializers

from comments.serializers import CommentSerializer
from users.serializers import UserSerializer
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # İç içe kullanıcı bilgisi (id değil, tam obje)
    author = UserSerializer(read_only=True)

    # Yorum sayısı (dinamik alan)
    comment_count = serializers.SerializerMethodField()

    # İlk 3 yorum (preview için)
    recent_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image',
            'comment_count', 'recent_comments',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        # Adım 9'da annotate ile optimize edeceğiz; şimdilik basit
        return obj.comments.filter(is_deleted=False).count()

    def get_recent_comments(self, obj):
        # En son 3 yorum, en yeni önce
        qs = obj.comments.filter(is_deleted=False).order_by('-created_at')[:3]
        return CommentSerializer(qs, many=True).data