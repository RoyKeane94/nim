from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
import json
try:
    import markdown2
except ImportError:
    # Fallback if markdown2 is not installed
    def markdown2_markdown(text, extras=None):
        return text
    markdown2 = type('obj', (object,), {'markdown': markdown2_markdown})

from .models import Post, Author, Book, NewsletterSubscriber
from .forms import PostForm, NewsletterForm


# Public Views

def home(request):
    """Homepage - chronological list of published posts"""
    posts = Post.objects.filter(is_published=True).order_by('-publish_date')
    return render(request, 'blog/home.html', {'posts': posts})


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
        commentary_html = markdown2.markdown(post.commentary, extras=['fenced-code-blocks'])
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

@login_required
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


@login_required
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


@login_required
def post_preview(request, post_id):
    """Preview how post will look when published"""
    post = get_object_or_404(Post, pk=post_id)
    
    # Convert commentary markdown to HTML
    try:
        commentary_html = markdown2.markdown(post.commentary, extras=['fenced-code-blocks'])
    except:
        commentary_html = post.commentary.replace('\n', '<br>')
    
    context = {
        'post': post,
        'commentary_html': commentary_html,
        'preview_mode': True,
    }
    return render(request, 'blog/post.html', context)


@login_required
@require_http_methods(["POST"])
def post_publish(request, post_id):
    """Publish a draft post"""
    post = get_object_or_404(Post, pk=post_id)
    post.is_published = True
    post.is_draft = False
    post.save()
    return redirect('write_dashboard')


@login_required
@require_http_methods(["POST"])
def post_unpublish(request, post_id):
    """Unpublish a post"""
    post = get_object_or_404(Post, pk=post_id)
    post.is_published = False
    post.save()
    return redirect('write_dashboard')


@login_required
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
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'saved_at': post.updated_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def write_login(request):
    """Login page for writing interface"""
    if request.user.is_authenticated:
        return redirect('write_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('write_dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/write/login.html', {'form': form})

