# Generated by Django 5.2.4 on 2025-07-05 08:24

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('experience', models.TextField(help_text='Describe your relevant work experience')),
                ('skills', models.TextField(help_text='Comma-separated list of skills (e.g., Python, Django, REST)')),
                ('resume_pdf', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Applicant',
                'verbose_name_plural': 'Applicants',
                'ordering': ['-created_at'],
            },
        ),
    ]
