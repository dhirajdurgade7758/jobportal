from elasticsearch_dsl import Document, Text, Keyword, Date, Float
from elasticsearch_dsl import connections

from .models import Job

# Connect to Elasticsearch
connections.create_connection(hosts=['http://localhost:9200'])

class JobDocument(Document):
    title = Text()
    company_name = Text()
    location = Keyword()
    job_type = Keyword()
    tags = Text()
    description = Text()
    salary = Float()
    posted_at = Date()

    class Index:
        name = 'jobs'

    def save(self, **kwargs):
        return super().save(**kwargs)


    @classmethod
    def from_django(cls, job):
        return cls(
            meta={'id': job.id},
            title=job.title,
            company_name=job.company_name,
            location=job.location,
            job_type=job.job_type,
            tags=job.tags,
            description=job.description,
            salary=job.salary,
            posted_at=job.posted_at,
        )
