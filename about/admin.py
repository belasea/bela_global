from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import (
    FAQ, 
    FAQCategory, 
    CookiePolicy,
    PersonalDataPolicy,
    Terms,
    LegalNotice,
    International
)

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(FAQ)
class FAQAdmin(SummernoteModelAdmin):
    summernote_fields = ('answer',)

    list_display = ('question', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    list_editable = ('order',)
    search_fields = ('question',)
    

@admin.register(CookiePolicy)
class CookiePolicyAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'is_active',)
    list_filter = ('name', 'is_active')
    search_fields = ('name',)


@admin.register(PersonalDataPolicy)
class PersonalDataPolicyAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'is_active',)
    list_filter = ('name', 'is_active')
    search_fields = ('name',)

@admin.register(Terms)
class TermsAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'is_active',)
    list_filter = ('name', 'is_active')
    search_fields = ('name',)

@admin.register(LegalNotice)
class LegalNoticeAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'is_active',)
    list_filter = ('name', 'is_active')
    search_fields = ('name',)
    
@admin.register(International)
class InternationalAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'is_active',)
    list_filter = ('name', 'is_active')
    search_fields = ('name',)