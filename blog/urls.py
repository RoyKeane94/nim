from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('library/', views.archive, name='library'),
    path('archive/', views.archive, name='archive'),  # kept for backwards compatibility
    path('series/<slug:book_slug>/', views.series_view, name='series'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Writing interface URLs
    path('write/', views.write_dashboard, name='write_dashboard'),
    path('write/login/', views.write_login, name='write_login'),
    path('write/post/new/', views.post_editor, {'post_id': None}, name='post_editor_new'),
    path('write/post/<int:post_id>/', views.post_editor, name='post_editor'),
    path('write/post/<int:post_id>/preview/', views.post_preview, name='post_preview'),
    path('write/post/<int:post_id>/publish/', views.post_publish, name='post_publish'),
    path('write/post/<int:post_id>/unpublish/', views.post_unpublish, name='post_unpublish'),
    path('write/post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('write/post/<int:post_id>/reference/', views.post_reference, name='post_reference'),
    path('write/autosave/', views.autosave, name='autosave'),
    path('write/autosave/<int:post_id>/', views.autosave, name='autosave'),
    path('write/create-author/', views.create_author, name='create_author'),
    path('write/create-book/', views.create_book, name='create_book'),
    path('write/create-guest/', views.create_guest, name='create_guest'),
    path('write/create-tag/', views.create_tag, name='create_tag'),
]

