from django.shortcuts import render
from .models import (
    FAQCategory,
    CookiePolicy,
    PersonalDataPolicy,
    Terms,
    LegalNotice,
    International
)


def faq_view(request):
    categories = FAQCategory.objects.prefetch_related('faqs').all()
    context = {
        'categories':categories,
    }
    return render(request, "about/faq.html", context)


def cookie_policy(request):
    cookie_data = CookiePolicy.objects.first()
    context = {
        "cookie_data": cookie_data
    }
    return render(request, "about/cookie_policy.html", context)


def personal_data_policy(request):
    personal_data = PersonalDataPolicy.objects.first()
    context = {
        "personal_data": personal_data
    }
    return render(request, "about/personal_data_policy.html", context)


def terms(request):
    terms_data = Terms.objects.first()
    context = {
        "terms_data": terms_data
    }
    return render(request, "about/terms.html", context)


def legal_notice(request):
    legal_notice_data = LegalNotice.objects.first()
    context = {
        "legal_notice_data": legal_notice_data
    }
    return render(request, "about/legal_notice.html", context)


def international(request):
    international_data = International.objects.first()
    context = {
        "international_data": international_data
    }
    return render(request, "about/international.html", context)