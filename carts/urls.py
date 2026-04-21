from django.urls import path
from .import views

urlpatterns = [
    path("cart_list/", views.cart_list, name="cart_list"),
    
]