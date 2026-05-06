from django.contrib import admin
from .models import  WarehouseOrderDetail

class WarehouseOrderDetailAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'request_by', 'timestamp', 'update')
    list_per_page = 20

    class Meta:
        model = WarehouseOrderDetail


admin.site.register(WarehouseOrderDetail, WarehouseOrderDetailAdmin)