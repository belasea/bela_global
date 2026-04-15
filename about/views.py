from django.shortcuts import render
from .models import (
    OurBackground, 
    OurGoal, 
    Facility,
)


def about_us(request):
    # Fetch the first (and likely only) entry
    background_data = OurBackground.objects.first()
    our_goal = OurGoal.objects.filter(is_active=True).order_by('order')[:3]
    facility = Facility.objects.filter(is_active=True)[:6]
    
    context = {
        'background_data': background_data,
        'our_goal': our_goal,
        'facility': facility
    }
    return render(request, "about/about_us.html", context)
