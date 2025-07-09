import csv
from io import TextIOWrapper

from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect, render
from .models import *

from django.urls import reverse
from django.utils.html import format_html

# jobs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Job, JobApplication, SavedJob

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ('applicant', 'applied_at', 'status_badge')
    fields = ('applicant', 'job_link', 'applied_at', 'status_badge', 'view_application')
    can_delete = False
    
    def job_link(self, obj):
        url = reverse('admin:jobs_job_change', args=[obj.job.id])
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    job_link.short_description = 'Job'
    
    def status_badge(self, obj):
        status_map = {
            'AP': ('secondary', 'Applied'),
            'RE': ('info', 'Reviewed'),
            'IN': ('primary', 'Interviewing'),
            'OF': ('success', 'Offer Extended'),
            'AC': ('success', 'Accepted'),
            'RJ': ('danger', 'Rejected'),
        }
        color, text = status_map.get(obj.status, ('secondary', 'Unknown'))
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def view_application(self, obj):
        url = reverse('admin:jobs_jobapplication_change', args=[obj.id])
        return format_html('<a href="{}" class="button">View</a>', url)
    view_application.short_description = 'Action'

    def has_add_permission(self, request, obj=None):
        return False

class SavedJobInline(admin.TabularInline):
    model = SavedJob
    extra = 0
    readonly_fields = ('user', 'created_at')
    fields = ('user', 'created_at')
    can_delete = True
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'job_type', 'salary', 'posted_at', 'application_count', 'saved_count')
    list_filter = ('job_type', 'posted_at')
    search_fields = ('title', 'company_name', 'location', 'tags')
    readonly_fields = ('posted_at', 'updated_at', 'application_count', 'saved_count')
    fieldsets = (
        (None, {
            'fields': ('title', 'company_name', 'location')
        }),
        ('Details', {
            'fields': ('job_type', 'salary', 'tags', 'description')
        }),
        ('Metadata', {
            'fields': ('posted_at', 'updated_at', 'application_count', 'saved_count')
        }),
    )
    inlines = [JobApplicationInline, SavedJobInline]
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'
    
    def saved_count(self, obj):
        return obj.saved_by.count()
    saved_count.short_description = 'Saved By'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_title', 'company', 'status_badge', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__username', 'job__title', 'job__company_name')
    readonly_fields = ('applied_at', 'status_badge')
    fieldsets = (
        (None, {
            'fields': ('applicant', 'job')
        }),
        ('Application Details', {
            'fields': ('resume', 'cover_letter', 'status_badge', 'notes')
        }),
        ('Metadata', {
            'fields': ('applied_at',)
        }),
    )
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'
    job_title.admin_order_field = 'job__title'
    
    def company(self, obj):
        return obj.job.company_name
    company.short_description = 'Company'
    company.admin_order_field = 'job__company_name'
    
    def status_badge(self, obj):
        status_map = {
            'AP': ('secondary', 'Applied'),
            'RE': ('info', 'Reviewed'),
            'IN': ('primary', 'Interviewing'),
            'OF': ('success', 'Offer Extended'),
            'AC': ('success', 'Accepted'),
            'RJ': ('danger', 'Rejected'),
        }
        color, text = status_map.get(obj.status, ('secondary', 'Unknown'))
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'applicant')



admin.site.register(SavedJob)