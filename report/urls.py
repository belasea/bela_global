from django.urls import path
from .import views

urlpatterns = [
    path('user-dashboard', views.user_dashboard, name="user-dashboard"),
    
    # Customer Report ==============================================
    path('customer-report/', views.customer_report, name='customer-report'),
    path('update-customer/<int:id>/', views.update_customer_report, name='update-customer-report'),
    path('delete-customer/<int:id>/', views.delete_customer_report, name='delete-customer-report'),
    path('export-customer-csv/', views.customer_report_csv, name='export-customer-csv'),

    # Report =============================================================
    path('sales-report/', views.sales_report, name="sales-report"),
    path('export-sales-report/', views.export_sales_report, name='export-sales-report'),
    path('annual-sales/', views.order_annual_sales, name='annual-sales'),
    
    # 
    path('pending-carts/', views.pending_carts, name="pending-carts")

]