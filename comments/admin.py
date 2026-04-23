from django.contrib import admin
from django.contrib import admin
from .models import (
    Comment,
    Reply
)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'approve')
    list_filter = ('approve', 'created_on')
    search_fields = ('name', 'email', 'body')
    list_editable = ['approve']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approve=True)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on', 'approve')
    list_filter = ('approve', 'created_on')
    search_fields = ('name', 'body')