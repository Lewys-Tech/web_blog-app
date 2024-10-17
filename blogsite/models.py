from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager

class Comment(models.Model):
    post=models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    name=models.CharField(max_length=80)
    email=models.EmailField()
    body=models.TextField()
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    active=models.BooleanField(default=True)
class Meta:
    ordering=['created']
    indexes=[models.Index(fields=['created']), ]
    def __str__(self):
        return f'Comment by{self.name} on {self.post}'

class Status(models.TextChoices):
    DRAFT = 'DF', 'Draft'
    PUBLISHED = 'PB', 'Published'

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.PUBLISHED)

class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')  # Ensure slugs are unique
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)  # Use Status.choices

    objects = models.Manager()  # Default Manager
    published = PublishedManager()  # Custom manager
    tags=TaggableManager()

    class Meta:
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish'])]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blogsite:post_detail_by_date', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])