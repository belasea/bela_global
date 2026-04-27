from django.urls import path
from . import views

urlpatterns = [
    
    path('checkout/', views.cart_checkout, name="checkout"),
    path('checkout-done/<slug:slug>/', views.checkout_done_view, name='checkout-done'),
    # path('create-pdf/<slug:slug>/', views.pdf_report_create, name='create-pdf'),

]