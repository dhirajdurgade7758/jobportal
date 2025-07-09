from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    
    # Professional Summary (AI-generated)
    summary = models.TextField(blank=True, null=True)
    
    # Work Experience (as JSON or separate model)
    work_experience = models.JSONField(default=list)  # Example: [{"job_title": "...", "company": "...", "years": "...", "description": "..."}]
    
    # Education
    education = models.JSONField(default=list)  # Example: [{"degree": "...", "university": "...", "years": "..."}]
    
    # Skills (comma-separated or JSON)
    skills = models.TextField(blank=True, null=True)  # "Python, Django, JavaScript, ..."
    
    # Additional Info
    certifications = models.TextField(blank=True, null=True)
    projects = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.full_name}'s Resume"
    