from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'active']
    list_editable = ('active',)
    search_fields = ['code']
    list_per_page = 20




