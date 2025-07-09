from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Job
from .search_indexes import JobDocument
from django.core.cache import cache
@receiver(post_save, sender=Job)
def index_job(sender, instance, **kwargs):
    doc = JobDocument.from_django(instance)
    doc.save()

    # Clear all cached search keys (or based on tags, title)
    cache.delete_pattern("search:*")

@receiver(post_delete, sender=Job)
def delete_job_from_index(sender, instance, **kwargs):
    try:
        JobDocument.get(id=instance.id).delete()
    except:
        pass

    cache.delete_pattern("search:*")
