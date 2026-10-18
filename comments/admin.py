from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'short_content', 'created_at')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('author__username', 'content')
    raw_id_fields = ('author', 'post')

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'İçerik'