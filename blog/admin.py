from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import (
    Category,
    Blog,
    Advertisement,
    Comment,
    Reply
)

@admin.register(Category)
class BlogAdmin(SummernoteModelAdmin):
    list_display = ('title', 'slug', 'timestamp')
    list_per_page = 20
    search_fields = ['title']

@admin.register(Blog)
class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('title', 'slug', 'timestamp')
    list_per_page = 20
    search_fields = ['title']

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_field', 'timestamp']
    list_per_page = 20
    search_fields = ['title']

    class Meta:
        model = Advertisement


admin.site.register(Advertisement, AdvertisementAdmin)


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