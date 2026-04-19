from django.shortcuts import render
from .models import Slider, SkincareSection
from products.models import HomeCategory


def home_view(request):
    # Fetch only active sliders ordered by your 'order' field
    sliders = Slider.objects.filter(is_active=True)
    skincare_data = SkincareSection.objects.filter(is_active=True).first()
    home_category = HomeCategory.objects.filter(is_active=True).prefetch_related('items')
    
    context = {
        'sliders': sliders,
        'skincare': skincare_data,
        'home_category': home_category
    }
    return render(request, "home/index.html", context)