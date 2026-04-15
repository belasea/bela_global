from django.contrib import admin
from .models import Notification, Subscribe

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message']

    class Meta:
        model = Notification


admin.site.register(Notification, NotificationAdmin)

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('email',)
