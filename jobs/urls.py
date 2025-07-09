from django.urls import path, include
from .views import *

urlpatterns = [
    path("", home_view, name="home"),  # ✅ Home page
    path("search/", job_search_view, name="job_search"),
    path("trending/", trending_queries_view, name="trending_queries"),
    path('resume/', include('resume_generator.urls')),
    path('jobs/<int:job_id>/save/', save_job, name='save_job'),
    path('saved-jobs/', saved_jobs, name='saved_jobs'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', apply_to_job, name='apply_job'),
    path('my-applications/', my_applications, name='my_applications'),

]
