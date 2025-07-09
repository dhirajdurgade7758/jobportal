from django.db import models

from jobportal import settings
from django.contrib.auth.models import User
# Choice options
JOB_TYPE_CHOICES = [
    ('FT', 'Full-Time'),
    ('PT', 'Part-Time'),
    ('IN', 'Internship'),
    ('CT', 'Contract'),
    ('FL', 'Freelance'),
]

class Job(models.Model):
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tags = models.CharField(max_length=255, help_text="Comma-separated tags (e.g., Python, Django, Remote)")
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saved_by = models.ManyToManyField(User, through='SavedJob', related_name='saved_jobs_through')

    @property
    def saved_by_users(self):
        return User.objects.filter(saved_jobs__job=self)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',')]
    
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('AP', 'Applied'),
        ('RE', 'Reviewed'),
        ('IN', 'Interviewing'),
        ('OF', 'Offer Extended'),
        ('AC', 'Accepted'),
        ('RE', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AP')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"

from django.db import models
from django.contrib.auth.models import User

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together = ('user', 'job')  # Prevent duplicate saves
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"