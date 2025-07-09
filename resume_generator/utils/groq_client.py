
import os
from groq import Groq
from django.conf import settings

def generate_resume_summary(user_data):
    """
    Generates a complete professional resume in Markdown format using GROQ AI.
    
    Args:
        user_data (dict): Contains resume details from the form submission
    
    Returns:
        str: AI-generated professional resume in Markdown format
    """
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    # Prepare the structured prompt with clear formatting instructions
    prompt = f"""
    Create a complete professional resume in Markdown format for {user_data.get('full_name', 'the candidate')} 
    using the following information. The output MUST use proper Markdown formatting for headings, 
    bullet points, and sections that will convert cleanly to PDF and also give only the resume content, no additional text or explanations 
    like 'Here is the resume in Markdown format give only and only resume'.

    --- BEGIN RESUME STRUCTURE INSTRUCTIONS ---
    # [Full Name]
    [Email] | [Phone] | [LinkedIn] | [Portfolio]
    
    ## Summary
    - 3-4 line professional overview highlighting key qualifications
    
    ## Technical Skills
    - Categorized list of skills
    
    ## Professional Experience
    ### [Job Title]  
    [Company Name] | [Years]  
    * Achievement 1 (quantified)
    * Achievement 2
    
    ## Education
    ### [Degree]  
    [University] | [Years]
    
    ## Certifications
    - [Certification 1 with description]
    - [Certification 2 with description]
    
    ## Projects
    - [Project 1 with description]
    - [Project 2 with description]
    --- END STRUCTURE INSTRUCTIONS ---

    --- BEGIN CANDIDATE DATA ---
    Name: {user_data.get('full_name', '')}
    Contact: {user_data.get('email', '')} | {user_data.get('phone', '')}
    LinkedIn: {user_data.get('linkedin_url', '')}
    Portfolio: {user_data.get('portfolio_url', '')}

    Skills: {', '.join(user_data.get('skills', []))}

    Work Experience:
    {format_work_experience(user_data.get('work_experience', []))}

    Education:
    {format_education(user_data.get('education', []))}

    Certifications: {user_data.get('certifications', 'None provided')}
    Projects: {user_data.get('projects', 'None provided')}
    --- END CANDIDATE DATA ---

    Additional Instructions:
    1. Use proper Markdown syntax throughout
    2. Keep consistent formatting for all sections
    3. Start all bullet points with action verbs (Designed, Implemented, Optimized)
    4. Quantify achievements where possible (e.g., "Increased performance by 40%")
    5. Never use pronouns (he/she/they)
    6. Ensure the resume looks polished when converted to PDF
    7. Include all provided sections even if some data is minimal
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=2500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating resume: {str(e)}")
        return f"# Resume Generation Error\nFailed to generate resume content. Error: {str(e)}"

def format_work_experience(experience_list):
    """Formats work experience for the prompt"""
    if not experience_list:
        return "No work experience provided"
    
    formatted = []
    for exp in experience_list:
        if not exp.get('job_title'):
            continue
        entry = [
            f"Job Title: {exp['job_title']}",
            f"Company: {exp.get('company', '')}",
            f"Years: {exp.get('years', '')}",
            f"Description: {exp.get('description', '')}"
        ]
        formatted.append("\n".join(entry))
    
    return "\n---\n".join(formatted)

def format_education(education_list):
    """Formats education for the prompt"""
    if not education_list:
        return "No education information provided"
    
    formatted = []
    for edu in education_list:
        if not edu.get('degree'):
            continue
        entry = [
            f"Degree: {edu['degree']}",
            f"Institution: {edu.get('university', '')}",
            f"Years: {edu.get('years', '')}"
        ]
        formatted.append("\n".join(entry))
    
    return "\n---\n".join(formatted)