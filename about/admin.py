from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import (
    OurBackground, 
    OurGoal, 
    Facility,
)



@admin.register(OurBackground)
class OurBackgroundAdmin(admin.ModelAdmin):
    list_display = ['title', 'years_experience',]


@admin.register(OurGoal)
class OurGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'is_active')  # show human-readable name and status
    list_filter = ('is_active',)                       # filter by active/inactive
    search_fields = ('name',)                          # search by choice key
    ordering = ('name',)  
