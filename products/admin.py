from django.contrib import admin
from django.utils.html import format_html
from .models import HomeCategory, HomeCategoryItem, Category, SubCategory



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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'timestamp', 'update')
    search_fields = ('title',)
    readonly_fields = ('slug', 'timestamp', 'update')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'slug', 'timestamp')
    list_display_links = ('thumbnail', 'title')
    search_fields = ('title',)
    readonly_fields = ('slug', 'timestamp', 'update')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    
    thumbnail.short_description = 'Preview'