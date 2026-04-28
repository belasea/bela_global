from django.urls import path
from . import views


urlpatterns = [
    # Crud Operations ==================================================
    path('inventory-list/', views.inventory_list, name='inventory-list'),
    path('add-inventory/',  views.add_inventory, name='add-inventory'),
    path('update-inventory/<int:id>/', views.update_inventory, name='update-inventory'),
    path('delete-inventory/<int:id>/', views.delete_inventory, name='delete-inventory'),

    # Download CSV =========================================================================
    path('inventory-by-date-csv/', views.inventory_by_date_csv, name='inventory-by-date-csv'),
    path('inventory_stock_csv/', views.inventory_stock_csv, name="inventory_stock_csv"),
    path('out-of-stock/', views.out_of_stock, name="out-of-stock"),
    path('out-of-stock-csv/', views.out_of_stock_csv, name="out-of-stock-csv"),
    path('check-stock-quantity/', views.check_stock_quantity, name="check-stock-quantity"), 
]