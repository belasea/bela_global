from django.urls import path
from .import views

urlpatterns = [
    path("blog/", views.blog, name="blog"),
    path('blog/category/<slug:slug>/', views.blog_category, name="blog-category"),
    path("blog-details/<slug:slug>/", views.blog_details, name="blog-details"),
]