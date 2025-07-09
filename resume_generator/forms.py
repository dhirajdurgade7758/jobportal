from django import forms
from .models import Resume
import json

class ResumeForm(forms.ModelForm):
    # Personal Info
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'full name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'email id'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'phone number'}))
    portfolio_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}))
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'})) 
    
    # Work Experience (Dynamic Fields - will be combined into JSON)
    job_title = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}))
    company = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}))
    years = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Years (e.g., 2020-2023)'}))
    job_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Key achievements (1 per line)', 'rows': 3}))
    
    # Skills
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Python, Django, PostgreSQL, AWS'}),
        help_text="Separate skills with commas",
        required=False
    )
    
    # Education (will be combined into JSON)
    degree = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'degree'}))
    university = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'university'}))
    education_years = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Years (e.g., 2018-2022)'}))
    
    # Additional Info
    certifications = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Certification details', 'rows': 3}))
    projects = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project details', 'rows': 3}))
    
    class Meta:
        model = Resume
        fields = ['full_name', 'email', 'phone', 'linkedin_url', 'portfolio_url', 'skills', 'certifications', 'projects']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Prepare work experience JSON
        work_experience = []
        if self.cleaned_data.get('job_title') or self.cleaned_data.get('company'):
            work_experience.append({
                'job_title': self.cleaned_data.get('job_title', ''),
                'company': self.cleaned_data.get('company', ''),
                'years': self.cleaned_data.get('years', ''),
                'description': self.cleaned_data.get('job_description', '')
            })
        instance.work_experience = work_experience
        
        # Prepare education JSON
        education = []
        if self.cleaned_data.get('degree') or self.cleaned_data.get('university'):
            education.append({
                'degree': self.cleaned_data.get('degree', ''),
                'university': self.cleaned_data.get('university', ''),
                'years': self.cleaned_data.get('education_years', '')
            })
        instance.education = education
        
        if commit:
            instance.save()
        return instance