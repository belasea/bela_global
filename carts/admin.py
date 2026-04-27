from django.contrib import admin
from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'timestamp', 'update')
    list_filter = ('owner', 'timestamp', 'update')
    search_fields = ['owner__username']
    list_per_page = 20

admin.site.register(Cart, CartAdmin)


class CartItemInline(admin.TabularInline):
    model = CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'timestamp', 'update']
    inlines = [CartItemInline]


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'quantity', 'price', 'weight_avg_cost', 'last_purchase_price', 'timestamp')

    def get_title(self, obj):
        if obj.product:
            return f'Product: {obj.product.title}'
        else:
            return 'Unknown Item'

    get_title.short_description = 'Title'

admin.site.register(CartItem, CartItemAdmin)