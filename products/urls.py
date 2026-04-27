from django.urls import path
from .import views

urlpatterns = [
    path("products/category/", views.category_view, name="category"),
    path('products/<slug:category_slug>/', views.product_category_view, name='product_category'),
    path('products/<slug:category_slug>/<slug:subcategory_slug>/', views.product_list_view, name='sub_category'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
]