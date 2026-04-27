from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Order, CancelledOrder, ReturnedOrder

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'shipping_address', 'status', 'total_product_price', 'timestamp')
    search_fields = ('order_id', 'user__username', 'shipping_address__full_address', 'timestamp')

admin.site.register(Order, OrderAdmin)


@admin.register(CancelledOrder)
class CancelledOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'added', 'timestamp', 'update', 'slug')
    search_fields = ['order__id', 'product__title', 'slug']
    list_filter = ('added', 'timestamp', 'update')


@admin.register(ReturnedOrder)
class ReturnedOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'loss', 'timestamp', 'update', 'slug')
    search_fields = ['order__id', 'slug']
    list_filter = ('timestamp', 'update')


