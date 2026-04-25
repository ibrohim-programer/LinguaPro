from django.contrib import admin
from .models import GroupMessage


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display  = ['id', 'group', 'sender', 'message_type', 'short_content', 'created_at']
    list_filter   = ['message_type', 'group', 'created_at']
    search_fields = ['content', 'sender__username', 'group__name']
    readonly_fields = ['created_at', 'updated_at', 'read_by']
    ordering      = ['-created_at']

    def short_content(self, obj):
        if obj.content:
            return obj.content[:60]
        return f'[{obj.message_type}]'
    short_content.short_description = 'Mazmun'