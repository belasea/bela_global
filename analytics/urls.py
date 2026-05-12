from django.urls import path
from . import views

urlpatterns = [
    path('user-dashboard/', views.user_dashboard, name="user-dashboard"),
    path('my-orders/', views.my_orders, name="my-orders"),
    
    # pending_carts =====================================================
    path('pending-carts/', views.pending_carts, name="pending-carts"),
    path('export_pending_carts/', views.export_pending_carts, name="export_pending_carts"),
    
    # user_object_view =====================================================
    path('user-object-view/', views.user_object_view, name='user-object-view'),
    path('download-user-object/', views.download_user_object, name='download-user-object'),
    path('user-session/', views.user_session, name="user-session")
]