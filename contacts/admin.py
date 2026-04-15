from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Contact, ReplayContact


# Contact CSV import and Export ============================================================
class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'subject',  'message']


class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource
    list_display = ['first_name', 'last_name', 'email']
    list_per_page = 20
    search_fields = ['first_name', 'email',]


admin.site.register(Contact, ContactAdmin)


# ReplayContactAdmin Admin ============================================================
class ReplayContactAdmin(admin.ModelAdmin):
    list_display = ["message"]
    
    class Meta:
        model = ReplayContact
        fields = ['id', 'message']
       
        
admin.site.register(ReplayContact, ReplayContactAdmin)