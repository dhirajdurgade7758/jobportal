from django.urls import path  
from . import views  

urlpatterns = [  
    path('', views.resume_home, name='resume_home'),  
    path('create/', views.generate_resume, name='resume_form'),
    path('preview/<int:resume_id>/pdf/', views.download_resume_pdf, name='resume_pdf'),
]  