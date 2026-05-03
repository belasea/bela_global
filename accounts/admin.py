from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'country', 'email', 'date_joined']
    search_fields = ['first_name', 'country', 'email', 'date_joined']
    list_filter = ('country',)
    list_per_page = 20

    class Meta:
        model = User


admin.site.register(User, UserAdmin)

