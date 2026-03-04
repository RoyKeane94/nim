from django.contrib import admin
from .models import Author, Book, Post, NewsletterSubscriber, Tag, Guest


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    filter_horizontal = ['tags']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'source_type', 'is_series', 'status', 'created_at']
    list_filter = ['source_type', 'is_series', 'status', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'author__name']
    raw_id_fields = ['author']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'book', 'publish_date', 'is_published', 'is_draft', 'created_at']
    list_filter = ['is_published', 'is_draft', 'publish_date', 'book__source_type', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'author__name', 'book__title']
    raw_id_fields = ['author', 'book']
    filter_horizontal = ['guests', 'tags']
    date_hierarchy = 'publish_date'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']

