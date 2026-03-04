from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count, Case, When, Value, IntegerField
from functools import wraps
import json
try:
    import markdown2
except ImportError:
    # Fallback if markdown2 is not installed
    def markdown2_markdown(text, extras=None):
        return text
    markdown2 = type('obj', (object,), {'markdown': markdown2_markdown})

from .models import Post, Author, Book, NewsletterSubscriber, Guest, Tag
from .forms import PostForm, NewsletterForm, AuthorForm, BookForm, GuestForm, TagForm


# Decorator to restrict access to superusers only
def superuser_required(view_func):
    """Decorator that checks if user is a superuser"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('write_login')
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access denied. Only superusers can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Public Views

def home(request):
    """Homepage - chronological list of published posts with sidebar data"""
    posts = (
        Post.objects.filter(is_published=True)
        .select_related('author', 'book')
        .prefetch_related('tags', 'guests')
        .order_by('-publish_date')
    )
    # Authors with published post count for "Browse by Author"
    authors_with_counts = (
        Author.objects.filter(posts__is_published=True)
        .annotate(post_count=Count('posts', distinct=True))
        .order_by('-post_count', 'name')
    )
    # Shelf: books for "Currently Reading" (in_progress first, then up_next, then complete)
    status_order = Case(
        When(status='in_progress', then=Value(0)),
        When(status='up_next', then=Value(1)),
        When(status='complete', then=Value(2)),
        default=Value(3),
        output_field=IntegerField(),
    )
    shelf_books = (
        Book.objects.filter(status__in=['in_progress', 'up_next', 'complete'])
        .select_related('author')
        .order_by(status_order, 'title')
    )[:6]
    context = {
        'posts': posts,
        'authors_with_counts': authors_with_counts,
        'shelf_books': shelf_books,
    }
    return render(request, 'blog/home.html', context)


def archive(request):
    """Archive page with filters"""
    posts = Post.objects.filter(is_published=True).order_by('-publish_date')
    authors = Author.objects.filter(posts__is_published=True).distinct().order_by('name')
    books = Book.objects.filter(posts__is_published=True).distinct().order_by('title')
    
    # Get filter parameters
    author_filter = request.GET.get('author')
    book_filter = request.GET.get('book')
    tab = request.GET.get('tab', 'recent')
    
    # Apply filters
    if author_filter:
        posts = posts.filter(author__slug=author_filter)
    if book_filter:
        posts = posts.filter(book__slug=book_filter)
    
    # Tab filtering
    if tab == 'archive':
        # All posts (already filtered)
        pass
    elif tab == 'authors':
        # Group by author - this would need custom logic
        pass
    
    context = {
        'posts': posts,
        'authors': authors,
        'books': books,
        'active_author': author_filter,
        'active_book': book_filter,
        'active_tab': tab,
    }
    return render(request, 'blog/archive.html', context)


def series_view(request, book_slug):
    """Series page showing all posts for a book"""
    book = get_object_or_404(Book, slug=book_slug)
    posts = book.posts.filter(is_published=True).order_by('series_order', 'publish_date')
    
    # Get previous/next series
    all_series = Book.objects.filter(is_series=True, posts__is_published=True).distinct()
    series_list = list(all_series)
    try:
        current_index = series_list.index(book)
        prev_series = series_list[current_index - 1] if current_index > 0 else None
        next_series = series_list[current_index + 1] if current_index < len(series_list) - 1 else None
    except ValueError:
        prev_series = None
        next_series = None
    
    context = {
        'book': book,
        'posts': posts,
        'prev_series': prev_series,
        'next_series': next_series,
    }
    return render(request, 'blog/series.html', context)


def post_detail(request, slug):
    """Individual post page"""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # Convert commentary markdown to HTML
    try:
        # Use markdown2 with blockquote support
        commentary_html = markdown2.markdown(
            post.commentary, 
            extras=['fenced-code-blocks', 'code-friendly']
        )
    except:
        commentary_html = post.commentary.replace('\n', '<br>')
    
    prev_post = post.get_previous_post()
    next_post = post.get_next_post()
    
    context = {
        'post': post,
        'commentary_html': commentary_html,
        'prev_post': prev_post,
        'next_post': next_post,
    }
    return render(request, 'blog/post.html', context)


@require_http_methods(["POST"])
def subscribe(request):
    """Newsletter subscription endpoint"""
    form = NewsletterForm(request.POST)
    if form.is_valid():
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=form.cleaned_data['email'],
            defaults={'is_active': True}
        )
        if not created:
            subscriber.is_active = True
            subscriber.save()
        return JsonResponse({'success': True, 'message': 'Thank you for subscribing!'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# Writing Interface Views

@superuser_required
def write_dashboard(request):
    """Writing dashboard - list all posts"""
    posts = Post.objects.all().order_by('-updated_at')
    
    # Filters
    filter_type = request.GET.get('filter', 'all')
    book_filter = request.GET.get('book')
    
    if filter_type == 'drafts':
        posts = posts.filter(is_draft=True)
    elif filter_type == 'published':
        posts = posts.filter(is_published=True)
    
    if book_filter:
        posts = posts.filter(book__slug=book_filter)
    
    books = Book.objects.all().order_by('title')
    
    context = {
        'posts': posts,
        'books': books,
        'filter_type': filter_type,
        'book_filter': book_filter,
    }
    return render(request, 'blog/write/dashboard.html', context)


@superuser_required
def post_editor(request, post_id=None):
    """Post editor - create or edit posts"""
    post = None
    if post_id is not None:
        post = get_object_or_404(Post, pk=post_id)
    
    # Get all posts for reference sidebar
    all_posts = Post.objects.all().order_by('-publish_date')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # Handle points from JSON
            points_json = request.POST.get('points', '[]')
            try:
                points = json.loads(points_json)
                # Ensure we have exactly 10 points (fill empty ones)
                while len(points) < 10:
                    points.append({'title': '', 'text': ''})
                points = points[:10]  # Limit to 10
                post.points = points
            except json.JSONDecodeError:
                post.points = []
            
            post.save()
            form.save_m2m()  # Save many-to-many: guests, tags
            return redirect('write_dashboard')
    else:
        form = PostForm(instance=post)
        if post and post.points:
            points = post.points
        else:
            points = [{'title': '', 'text': ''} for _ in range(10)]
    
    context = {
        'form': form,
        'post': post,
        'all_posts': all_posts,
        'points': points,
        'authors': Author.objects.all().order_by('name'),
        'books': Book.objects.all().order_by('title'),
    }
    return render(request, 'blog/write/editor.html', context)


@superuser_required
def post_preview(request, post_id):
    """Preview how post will look when published"""
    post = get_object_or_404(Post, pk=post_id)
    
    # Convert commentary markdown to HTML
    try:
        # Use markdown2 with blockquote support
        commentary_html = markdown2.markdown(
            post.commentary, 
            extras=['fenced-code-blocks', 'code-friendly']
        )
    except:
        commentary_html = post.commentary.replace('\n', '<br>')
    
    context = {
        'post': post,
        'commentary_html': commentary_html,
        'preview_mode': True,
    }
    return render(request, 'blog/post.html', context)


@superuser_required
@require_http_methods(["POST"])
def post_publish(request, post_id):
    """Publish a draft post"""
    post = get_object_or_404(Post, pk=post_id)
    post.is_published = True
    post.is_draft = False
    post.save()
    return redirect('write_dashboard')


@superuser_required
@require_http_methods(["POST"])
def post_unpublish(request, post_id):
    """Unpublish a post"""
    post = get_object_or_404(Post, pk=post_id)
    post.is_published = False
    post.save()
    return redirect('write_dashboard')


@superuser_required
@require_http_methods(["POST"])
def autosave(request, post_id=None):
    """Auto-save endpoint for AJAX"""
    try:
        data = json.loads(request.body)
        
        if post_id:
            post = get_object_or_404(Post, pk=post_id)
        else:
            # Create new post with minimal required fields
            post = Post()
            # Set defaults if creating new
            if not data.get('title'):
                return JsonResponse({'success': False, 'error': 'Title required for new post'}, status=400)
        
        # Update post fields
        if 'title' in data and data['title']:
            post.title = data['title']
        if 'publish_date' in data and data['publish_date']:
            post.publish_date = data['publish_date']
        if 'author_id' in data and data['author_id']:
            try:
                post.author_id = int(data['author_id'])
            except (ValueError, TypeError):
                pass
        if 'book_id' in data and data['book_id']:
            try:
                post.book_id = int(data['book_id'])
            except (ValueError, TypeError):
                pass
        if 'series_order' in data and data['series_order']:
            try:
                post.series_order = int(data['series_order'])
            except (ValueError, TypeError):
                post.series_order = None
        if 'points' in data:
            post.points = data['points']
        if 'commentary' in data:
            post.commentary = data['commentary']
        
        post.save()
        
        # Many-to-many: guests and tags (only for existing posts)
        if post.pk:
            if 'guest_ids' in data and isinstance(data['guest_ids'], list):
                try:
                    ids = [int(x) for x in data['guest_ids'] if x]
                    post.guests.set(ids)
                except (ValueError, TypeError):
                    pass
            if 'tag_ids' in data and isinstance(data['tag_ids'], list):
                try:
                    ids = [int(x) for x in data['tag_ids'] if x]
                    post.tags.set(ids)
                except (ValueError, TypeError):
                    pass
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'saved_at': post.updated_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@superuser_required
@require_http_methods(["POST"])
def create_author(request):
    """Create a new author via AJAX"""
    try:
        data = json.loads(request.body)
        form = AuthorForm(data)
        if form.is_valid():
            author = form.save()
            return JsonResponse({
                'success': True,
                'author': {
                    'id': author.id,
                    'name': author.name,
                    'slug': author.slug
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@superuser_required
@require_http_methods(["POST"])
def create_book(request):
    """Create a new book via AJAX"""
    try:
        data = json.loads(request.body)
        form = BookForm(data)
        if form.is_valid():
            book = form.save()
            return JsonResponse({
                'success': True,
                'book': {
                    'id': book.id,
                    'title': book.title,
                    'slug': book.slug,
                    'author_id': book.author_id
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@superuser_required
@require_http_methods(["POST"])
def create_guest(request):
    """Create a new guest via AJAX"""
    try:
        data = json.loads(request.body)
        form = GuestForm(data)
        if form.is_valid():
            guest = form.save()
            return JsonResponse({
                'success': True,
                'guest': {
                    'id': guest.id,
                    'name': guest.name,
                    'slug': guest.slug
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@superuser_required
@require_http_methods(["POST"])
def create_tag(request):
    """Create a new tag via AJAX"""
    try:
        data = json.loads(request.body)
        form = TagForm(data)
        if form.is_valid():
            tag = form.save()
            return JsonResponse({
                'success': True,
                'tag': {
                    'id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def write_login(request):
    """Login page for writing interface - superusers only"""
    # If already logged in as superuser, redirect to dashboard
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('write_dashboard')
    
    # If logged in but not superuser, show error
    if request.user.is_authenticated and not request.user.is_superuser:
        return render(request, 'blog/write/login.html', {
            'form': AuthenticationForm(),
            'error': 'Access denied. Only superusers can access the writing interface.'
        })
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Check if user is superuser after login
            if user.is_superuser:
                return redirect('write_dashboard')
            else:
                # Log out non-superuser and show error
                from django.contrib.auth import logout
                logout(request)
                return render(request, 'blog/write/login.html', {
                    'form': AuthenticationForm(),
                    'error': 'Access denied. Only superusers can access the writing interface.'
                })
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/write/login.html', {'form': form})

