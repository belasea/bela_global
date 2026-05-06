from django.contrib import admin
from .models import (
    Inventory, 
    InventoryStock,
    InventoryTransaction
)
from import_export import resources
from import_export.admin import ImportExportModelAdmin


admin.site.register(InventoryTransaction)


class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory
        fields = ('id', 'pro_id',  'pro_id__title', 'purchase_date', 'quantity_cost',
                  'purchase_quantity', 'stock_quantity', 'damage_quantity',
                  'misconduct', 'seller', 'quantity_updated')


class InventoryAdmin(ImportExportModelAdmin):
    resource_class = InventoryResource

    list_display = [
        'get_id', 'get_title', 'country', 'purchase_date', 'seller', 'quantity_cost', 'purchase_quantity',  
        'stock_quantity', 'quantity_updated',
    ]
    list_filter = ('country',)
    search_fields = ['pro_id__title', 'seller']
    list_editable = ['purchase_quantity', 'country', 'stock_quantity', 'quantity_cost', 'quantity_updated']
    list_per_page = 20
    ordering = ['-purchase_date']

    def get_id(self, obj):
        return obj.pro_id

    def get_title(self, obj):
        return obj.pro_id.title

    get_id.admin_order_field = 'pro_id'
    get_id.short_description = 'Product ID'

    get_title.short_description = 'Title'
    get_title.admin_order_field = 'pro_id__title'


admin.site.register(Inventory, InventoryAdmin)


class InventoryStockResource(resources.ModelResource):
    class Meta:
        model = InventoryStock
        fields = ('id', 'pro_id__id', 'pro_id__title', 'stock_quantity')


class InventoryStockAdmin(ImportExportModelAdmin):
    resource_class = InventoryStockResource
    list_display = [
        'id', 'pro_id', 'country', 'get_title', 'stock_quantity'
    ]
    # list_editable = ['stock_quantity']
    readonly_fields = ['stock_quantity']
    list_per_page = 20
    list_filter = ('country',)
    search_fields = ['pro_id__title', 'pro_id__id']

    def get_id(self, obj):
        return obj.pro_id

    def get_title(self, obj):
        return obj.pro_id.title

    get_id.admin_order_field = 'pro_id'
    get_id.short_description = 'Product ID'

    get_title.short_description = 'Title'
    get_title.admin_order_field = 'pro_id__title'


admin.site.register(InventoryStock, InventoryStockAdmin) 