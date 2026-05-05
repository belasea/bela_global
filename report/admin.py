from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import CustomerReport

class CustomerReportResource(resources.ModelResource):
    class Meta:
        model = CustomerReport
        fields = [
            'id', 'order', 'order_conf_date', 'shipping_method',
            'bKash_payment_digit', 'customer_type', 'notes', 'delivery_conformations',
            'order__slug',
        ]


# Download and upload-content import and Export Files
class CustomerReportAdmin(ImportExportModelAdmin):
    resource_class = CustomerReportResource
    list_display = [
        'id', 'order', 'country', 'notes', 'customer_type',
    ]
    list_per_page = 20
    search_fields = [
        'id', 'notes', 'country',
    ]
    list_filter = ('country',)


admin.site.register(CustomerReport, CustomerReportAdmin)