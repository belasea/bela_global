from django.urls import path
from .import views

urlpatterns = [
    path("faq/", views.faq_view, name="faq"),
    path("cookie-policy/", views.cookie_policy, name="cookie-policy"),
    path("personal-data-policy/", views.personal_data_policy, name="personal-data-policy"),
    path("terms/", views.terms, name="terms"),
    path("legal-notice/", views.legal_notice, name="legal-notice"),
    path("international/", views.international, name="international"),
    
]