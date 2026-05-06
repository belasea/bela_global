from django.urls import path
from . import views

urlpatterns = [
   
    # Warehouse
    path('warehouse-list/', views.warehouse_list, name='warehouse-list'),
    path('add-warehouse/', views.add_warehouse, name='add-warehouse'),
    path('update-warehouse/<int:id>/', views.update_warehouse, name='update-warehouse'),
    path('delete-warehouse/<int:id>/', views.delete_warehouse, name='delete-warehouse'),
    path('export-warehouse-csv/', views.export_warehouse_csv, name='export-warehouse-csv'),

    path('normal-product-summary/', views.normal_product_summary, name="normal-product-summary"),
    path('export-today-product-summary/', views.export_today_product_summary, name="export-today-product-summary"),
    path('product-summary-by-date-csv', views.product_summary_by_date_csv, name="product-summary-by-date-csv"),
]