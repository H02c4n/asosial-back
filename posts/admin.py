from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_content', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('author__username', 'content')
    raw_id_fields = ('author',)      # dropdown yerine id arama (daha hızlı)

    def short_content(self, obj):
        return obj.content[:50]
    short_content.short_description = 'İçerik'