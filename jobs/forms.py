from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'resume': 'Upload your resume (PDF only)',
            'cover_letter': 'Cover Letter'
        }