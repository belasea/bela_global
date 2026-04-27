from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin
from .models import (
    HomeCategory, 
    HomeCategoryItem, 
    Category, 
    SubCategory, 
    Product
)

@admin.register(HomeCategory)
class HomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active', 'slug')
    list_editable = ('display_order', 'is_active')
    # Use prepopulated if you want to see it happen live, 
    # but ensure 'slug' is NOT in readonly_fields.
    prepopulated_fields = {"slug": ("name",)}

@admin.register(HomeCategoryItem)
class HomeCategoryItemAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'home_category', 'card_color', 'display_order')
    list_filter = ('home_category', 'card_color')
    search_fields = ('title', 'sub_title')
    list_editable = ('display_order', 'card_color')

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 4px;"/>', obj.image.url)
        return "No Image"
    thumbnail_preview.short_description = 'Image'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'timestamp')
    search_fields = ('title',)
    # Removed 'slug' from readonly so prepopulated_fields works
    readonly_fields = ('timestamp', 'update')
    prepopulated_fields = {"slug": ("title",)}



@admin.register(SubCategory)
class SubCategoryAdmin(SummernoteModelAdmin):
    summernote_fields = (
        'description', 
        'right_for_me', 
        'dermatologist_advice', 
        'range_details'
    )
    list_display = ('title', 'category', 'slug', 'product_count')
    list_filter = ('category',)
    search_fields = ('title',)
    readonly_fields = ('timestamp', 'update')
    prepopulated_fields = {"slug": ("title",)}

    def product_count(self, obj):
        return obj.products.count()
    
    product_count.short_description = 'Total Products'


@admin.register(Product)
class ProductAdmin(SummernoteModelAdmin):
    summernote_fields = ('description', )
    list_display = ('title', 'category', 'sub_category', 'price', 'active')
    list_filter = ('active', 'category', 'sub_category')
    list_editable = ('price', 'active')
    search_fields = ('title', 'slug')
    readonly_fields = ('timestamp', 'update')
    prepopulated_fields = {"slug": ("title",)}

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Img'