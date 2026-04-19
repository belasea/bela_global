from django.shortcuts import render
from .models import Slider, SkincareSection

def home_view(request):
    # Fetch only active sliders ordered by your 'order' field
    sliders = Slider.objects.filter(is_active=True)
    skincare_data = SkincareSection.objects.filter(is_active=True).first()
    
    context = {
        'sliders': sliders,
        'skincare': skincare_data,
    }
    return render(request, "home/index.html", context)