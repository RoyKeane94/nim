from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    SOURCE_TYPES = [
        ('book', 'Book'),
        ('podcast', 'Podcast'),
        ('essay', 'Essay'),
        ('other', 'Other')
    ]
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('complete', 'Complete')
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    description = models.TextField(blank=True)  # Italic description for series page
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, default='book')
    is_series = models.BooleanField(default=False)  # Can have multiple posts
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('series', kwargs={'book_slug': self.slug})
    
    def get_chapters_count(self):
        return self.posts.filter(is_published=True).count()
    
    class Meta:
        ordering = ['title']


class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='posts')
    
    # For series posts (e.g., Chapter 3)
    series_order = models.IntegerField(null=True, blank=True)
    
    publish_date = models.DateField()
    
    # Worth Stealing points (stored as JSON)
    points = models.JSONField(default=list)  # List of dicts: [{"title": "...", "text": "..."}]
    
    # Commentary
    commentary = models.TextField()
    
    # Status
    is_published = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def get_previous_post(self):
        return Post.objects.filter(
            is_published=True,
            publish_date__lt=self.publish_date
        ).order_by('-publish_date').first()
    
    def get_next_post(self):
        return Post.objects.filter(
            is_published=True,
            publish_date__gt=self.publish_date
        ).order_by('publish_date').first()
    
    class Meta:
        ordering = ['-publish_date']


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']

