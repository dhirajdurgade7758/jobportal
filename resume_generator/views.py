from django.shortcuts import render  
from django.contrib.auth.decorators import login_required
@login_required
def resume_home(request):  
    return render(request, 'resume_generator/resume_home.html')  


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ResumeForm
from .utils.groq_client import generate_resume_summary
from .models import Resume

@login_required
def generate_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            # Prepare structured data for GROQ
            resume_data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'] or None,
                'linkedin_url': form.cleaned_data['linkedin_url'] or None,
                'portfolio_url': form.cleaned_data['portfolio_url'] or None,
                'work_experience': [],
                'skills': [skill.strip() for skill in form.cleaned_data['skills'].split(',') if skill.strip()],
                'education': [],
                'certifications': form.cleaned_data['certifications'] or None,
                'projects': form.cleaned_data['projects'] or None
            }

            # Process work experience (now from single fields in form)
            if form.cleaned_data.get('job_title') or form.cleaned_data.get('company'):
                resume_data['work_experience'].append({
                    'job_title': form.cleaned_data['job_title'],
                    'company': form.cleaned_data['company'],
                    'years': form.cleaned_data['years'],
                    'description': form.cleaned_data['job_description']
                })

            # Process education
            if form.cleaned_data.get('degree') or form.cleaned_data.get('university'):
                resume_data['education'].append({
                    'degree': form.cleaned_data['degree'],
                    'university': form.cleaned_data['university'],
                    'years': form.cleaned_data['education_years']
                })

            # Generate AI resume content
            try:
                ai_content = generate_resume_summary(resume_data)
                print(ai_content)
            except Exception as e:
                messages.error(request, f"AI generation failed: {str(e)}")
                return redirect('resume_form')
            
            # Save to database
            resume = form.save(commit=False)
            resume.user = request.user
            resume.summary = ai_content
            
            # Convert skills list to comma-separated string
            resume.skills = ', '.join(resume_data['skills'])
            
            # Set JSON fields
            resume.work_experience = resume_data['work_experience']
            resume.education = resume_data['education']
            
            resume.save()
            
            return render(request, 'resume_generator/resume_preview.html', {
                'resume_text': ai_content,
                'resume_id': resume.id,
                'resume': resume  # Pass the full resume object to template
            })

    else:
        form = ResumeForm()
    
    return render(request, 'resume_generator/resume_form.html', {'form': form})



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.conf import settings
import markdown
from io import BytesIO
from xhtml2pdf import pisa
from .models import Resume

@login_required
def download_resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(resume.summary)
    
    # Create a complete HTML document with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{resume.full_name}'s Resume</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            h1 {{ color: #333366; }}
            .section {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="section">
            {html_content}
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.full_name}_Resume.pdf"'
    
    # Create PDF
    pdf_status = pisa.CreatePDF(
        full_html,  # Now passing a proper HTML string, not a set
        dest=response,
        encoding='UTF-8'
    )
    
    if pdf_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response