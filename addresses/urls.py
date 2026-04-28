from django.urls import path, include
from addresses.views import (
    billing_addresses_view,
    address_create_form,
    updated_user_address,
    delete_user_address,
    address_csv_by_date,
    all_user_address_csv,
)

urlpatterns = [
    path('billing-addresses/', billing_addresses_view, name='billing-addresses'),
    path('address-create/', address_create_form, name='address-create'),
    path('address-update/<int:id>/', updated_user_address, name='address-update'),
    path('address-delete/<int:id>/', delete_user_address, name='address-delete'),
    path('address-csv-by-date/', address_csv_by_date, name='address-csv-by-date'),
    path('all-user-address-csv/', all_user_address_csv, name='all-user-address-csv'),
]