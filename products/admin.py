from django.contrib import admin
from .models import HomeCategory, HomeCategoryItem



@admin.register(HomeCategory)
class HomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(HomeCategoryItem)
class HomeCategoryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'card_color', 'display_order')
    list_filter = ('card_color',)
    search_fields = ('title', 'short_description')
    list_editable = ('display_order',)