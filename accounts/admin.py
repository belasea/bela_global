from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User, Country


# Country CSV import and Export ======================
class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        fields = ('id', 'name', 'iso_code',)


class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource
    list_display = ('name', 'iso_code',)
    list_per_page = 20
    search_fields = ('name', 'iso_code',)


admin.site.register(Country, CountryAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'country', 'email', 'date_joined']
    search_fields = ['first_name', 'country', 'email', 'date_joined']
    list_filter = ('country',)
    list_per_page = 20

    class Meta:
        model = User


admin.site.register(User, UserAdmin)

