from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Address

class AddressResource(resources.ModelResource):
    class Meta:
        model = Address
        fields = ('first_name', 'last_name', 'email', 'contact_number', 'address_type', 'address', 'city', 'location')

class AddressAdmin(ImportExportModelAdmin):
    resource_class = AddressResource

    search_fields = ['first_name', 'country', 'email', 'contact_number', 'address', 'city', 'location']
    list_display = ['first_name', 'country', 'email', 'contact_number', 'timestamp']
    list_per_page = 20

admin.site.register(Address, AddressAdmin)