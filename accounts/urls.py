from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/<int:id>/', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password reset views
    path('reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/register/password_reset.html',
        email_template_name='accounts/register/password_reset_email.html',
        subject_template_name='accounts/register/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/register/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/register/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/register/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Password change views
    path('settings/password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/register/password_change.html'
    ), name='password_change'),
    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/register/password_change_done.html'
    ), name='password_change_done'),

    
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('export_users_csv/', views.export_users_csv, name='export_users_csv'),
]

