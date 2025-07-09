from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from elasticsearch_dsl.query import MultiMatch
from .search_indexes import JobDocument
import json
import logging
from django.contrib.auth.decorators import login_required
from .models import *

logger = logging.getLogger(__name__)
from django_redis import get_redis_connection  # Add this import at the top

@login_required
def job_search_view(request):
    query = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))
    suggestions_mode = request.GET.get("suggestions") == "1"
    per_page = 10
    results = []

    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user)
                       .values_list('job_id', flat=True))

    if suggestions_mode:
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        try:
            search_query = JobDocument.search()[0:15]
            search_query = search_query.query(
                "bool",
                should=[
                    {"match_phrase_prefix": {"title": {"query": query, "boost": 3}}},
                    {"match_phrase_prefix": {"company_name": {"query": query, "boost": 2}}},
                    {"prefix": {"tags": {"value": query, "boost": 1}}}
                ],
                minimum_should_match=1
            )
            response = search_query.execute()
            
            suggestions = []
            seen = set()
            
            for hit in response.hits:
                if query.lower() in hit.title.lower() and hit.title not in seen:
                    suggestions.append(hit.title)
                    seen.add(hit.title)
                    if len(suggestions) >= 8:
                        break
            
            if len(suggestions) < 8:
                for hit in response.hits:
                    if query.lower() in hit.company_name.lower() and hit.company_name not in seen:
                        suggestions.append(hit.company_name)
                        seen.add(hit.company_name)
                        if len(suggestions) >= 8:
                            break
            
            if len(suggestions) < 8:
                for hit in response.hits:
                    for tag in hit.tags:
                        if query.lower() in tag.lower() and tag not in seen:
                            suggestions.append(tag)
                            seen.add(tag)
                            if len(suggestions) >= 8:
                                break
                    if len(suggestions) >= 8:
                        break
            
            return JsonResponse({'suggestions': suggestions[:8]})
        
        except Exception as e:
            logger.error(f"Elasticsearch suggestions error: {e}")
            return JsonResponse({'suggestions': []})

    if query:
        redis_query_key = f"search:{query.lower()}:page:{page}"
        redis_freq_key = "search:frequency"

        # Try cache first
        cached_data = cache.get(redis_query_key)
        if cached_data:
            results = json.loads(cached_data)
        else:
            try:
                search_query = JobDocument.search().query(
                    MultiMatch(
                        query=query,
                        fields=["title", "company_name", "tags", "description"],
                        fuzziness="auto"
                    )
                )
                start = (page - 1) * per_page
                end = page * per_page
                search_query = search_query[start:end]
                response = search_query.execute()

                results = [
                    {
                        "id": hit.meta.id,
                        "title": hit.title,
                        "company_name": hit.company_name,
                        "location": hit.location,
                        "job_type": hit.job_type,
                        "tags": hit.tags,
                        "description": hit.description,
                    }
                    for hit in response.hits
                ]

                cache.set(redis_query_key, json.dumps(results), timeout=60 * 5)

            except Exception as e:
                logger.error(f"Elasticsearch error: {e}")
                results = []

        # Track keyword frequency using direct Redis connection
        try:
            redis_conn = get_redis_connection("default")
            # Increment score by 1 for this query
            redis_conn.zincrby(redis_freq_key, 1, query.lower())
            # Set expiration on the key (30 days)
            redis_conn.expire(redis_freq_key, 60 * 60 * 24 * 30)
        except Exception as e:
            logger.error(f"Redis error tracking search frequency: {e}")

    context = {
        "saved_job_ids": saved_job_ids,
        "results": results,
        "query": query,
        "page": page,
        "next_page": page + 1,
        "prev_page": page - 1 if page > 1 else None
    }

    return render(request, "jobs/search.html", context)

@login_required
def trending_queries_view(request):
    try:
        redis_conn = get_redis_connection("default")
        # Get top 20 queries with their scores
        top_queries = redis_conn.zrevrange("search:frequency", 0, 19, withscores=True)
        # Convert from bytes to strings and filter out queries with at least 2 searches
        print(f"Top queries from Redis: {top_queries}")
        trending = [
            (query.decode('utf-8'), int(score))
            for query, score in top_queries
            if int(score) >= 2  # Only show queries searched at least twice
        ]
        # Sort by score descending (though zrevrange already returns sorted)
        trending.sort(key=lambda x: x[1], reverse=True)
        print(f"Trending queries: {trending}")
    except Exception as e:
        logger.error(f"Redis error fetching trending queries: {e}")
        trending = []

    return render(request, "jobs/trending.html", {"trending_queries": trending})

@login_required
def home_view(request):
    return render(request, "jobs/home.html")

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Job, SavedJob

@login_required
def save_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=job_id)
        
        try:
            saved_job, created = SavedJob.objects.get_or_create(
                user=request.user,
                job=job
            )
            
            if not created:
                saved_job.delete()
                # Clear relevant cache
                cache_keys = cache.keys(f"search:*:job:{job_id}")
                for key in cache_keys:
                    cache.delete(key)
                    
                return JsonResponse({
                    'success': True,
                    'saved': False,
                    'message': 'Job removed from saved jobs',
                    'action': 'removed'
                })
            
            # Clear relevant cache
            cache_keys = cache.keys(f"search:*:job:{job_id}")
            for key in cache_keys:
                cache.delete(key)
                
            return JsonResponse({
                'success': True,
                'saved': True,
                'message': 'Job saved successfully',
                'action': 'saved'
            })
            
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Error processing your request'
            }, status=500)
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def saved_jobs(request):
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'jobs/saved_jobs.html', {
        'saved_jobs': saved_jobs,
        'active_tab': 'saved_jobs'
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, SavedJob

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    similar_jobs = Job.objects.filter(
    tags__icontains=job.tags.split(',')[0]  # Just as an example, to match the first tag
    ).exclude(id=job.id).order_by('-posted_at')[:4]

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'is_saved': is_saved,
        'similar_jobs': similar_jobs,
        'active_tab': 'job_detail'
    })

from django.shortcuts import redirect
from django.contrib import messages
from .forms import *

@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job')
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('my_applications')
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job,
        'active_tab': 'apply_job'
    })

@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    return render(request, 'jobs/my_applications.html', {
        'applications': applications,
        'active_tab': 'my_applications'
    })