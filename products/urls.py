from django.urls import path
from .import views

urlpatterns = [
    path("products/category/", views.category_view, name="category"),
    path('products/<slug:category_slug>/', views.product_category_view, name='product_category'),
    path('products/<slug:category_slug>/<slug:subcategory_slug>/', views.product_list_view, name='sub_category'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('comment-action/<str:item_type>/<int:item_id>/', views.edit_comment_item, name='comment_action'),
    path('delete-item/<str:item_type>/<int:item_id>/', views.delete_comment_item, name='delete_comment_item'),
    path('search/', views.search_view, name="search"),
]