from django.urls import path
from .import views

urlpatterns = [
    path("category_list/", views.category_list, name="category_list"),
    path('products/<slug:category_slug>/', views.product_category, name='product_category'),
    path("product_details/", views.product_details, name="product_details"),
]