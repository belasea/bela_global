from django.urls import path
from .import views

urlpatterns = [
    path('user-dashboard', views.user_dashboard, name="user-dashboard")
]