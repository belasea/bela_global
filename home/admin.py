from django.contrib import admin
from django.utils.html import format_html
from .models import Slider, SkincareSection

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    # What shows up in the list view
    list_display = ('title', 'label', 'order', 'is_active', 'image_preview')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'label', 'subtitle')

    # Function to show a small thumbnail in the admin list
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = 'Preview'


@admin.register(SkincareSection)
class SkincareSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)
 
    # Optional: If you want image previews in the detail page, you can add them as readonly_fields
    readonly_fields = ('left_preview',)

    def left_preview(self, obj):
        if obj.left_img_a:
            return format_html('<img src="{}" width="100" />', obj.left_img_a.url)
        return ""