from django.urls import path
from . import views

urlpatterns = [
    
    path('checkout/', views.cart_checkout, name="checkout"),
    path('checkout-done/<slug:slug>/', views.checkout_done_view, name='checkout-done'),
    path('create-pdf/<slug:slug>/', views.pdf_report_create, name='create-pdf'),
    path('order-pdf-list/', views.order_pdf_list, name='order-pdf-list'),
    
    path('order-csv-by-date/', views.order_csv_by_date, name="order-csv-by-date"),
    path('download-order/', views.download_order, name="download-order"),
    path('order-details/<slug:slug>/', views.order_details_view, name='order-details'),
    path('update-order/<slug:slug>/', views.update_order_view, name='update-order'),
    path('remove-product/', views.remove_product_order_list, name='remove-product'),
    path('order-remove-item/<int:order_id>/', views.order_remove_item, name='order-remove-item'),

    # Order Cancelled Item ======================================================================
    path('cancelled-order/<slug:order_slug>/', views.cancelled_order_view, name='cancelled-order'),
    path('add-product-inventory/', views.add_product_inventory, name='add-product-inventory'),
    path('cancelled-orders-list/', views.cancelled_orders_list, name='cancelled-orders-list'),
    path('cancelled-orders-details/', views.cancelled_order_details, name='cancelled-orders-details'),
    path('cancelled-orders-details-csv/', views.cancelled_order_details_csv, name='cancelled-orders-details-csv'),

    # Return Order ===================================================================
    path('create-returned-order/<slug:slug>/', views.create_returned_order, name="create-returned-order"),
    path('returned-order-list/', views.returned_order_list_view, name="returned-order-list"),
    path('returned-order-details-csv/', views.returned_order_details_csv, name="returned-order-details-csv")
]