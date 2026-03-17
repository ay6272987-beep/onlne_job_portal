from django.contrib import admin
from .models import UserProfile, Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title','company','location','job_type','posted_by','created_at','is_active']
    list_filter = ['job_type','is_active']
    search_fields = ['title','company']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant','job','status','applied_at']
    list_filter = ['status']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','role','company_name','phone']
