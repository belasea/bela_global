from django.urls import path
from . import views

urlpatterns = [
    path('coupon-apply/', views.coupon_apply, name="coupon-apply"),
    path('coupon/remove/', views.coupon_remove, name='coupon-remove'),
]