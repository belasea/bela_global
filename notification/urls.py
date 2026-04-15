from django.urls import path
from . import views

urlpatterns = [
    path('notification/', views.notification_list, name="notification"),
    path('read-notification/<int:pk>/', views.read_notification, name='read-notification'),
    path('delete-notification/<int:id>/', views.delete_notification, name="delete-notification"),
    
    path("subscribe/", views.subscribe_list, name="subscribe"),
    path('delete-subscribe/<int:id>/', views.delete_subscribe, name="delete-subscribe"),
    
    path('export_subscribe_csv/', views.export_subscribe_csv, name='export_subscribe_csv'),
    path('export_subscribe_by_date/', views.export_subscribe_csv_by_date, name='export_subscribe_by_date'),
]
