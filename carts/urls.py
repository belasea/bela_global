from django.urls import path
from .import views

urlpatterns = [
    
    path('cart-list/', views.cart_list, name="cart-list"),
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('increase-quantity/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove-cart-item/<int:cart_item_id>/', views.remove_cart_item, name='remove-cart-item'),
]