# Notes in the Margin - Django Blog

A minimalist blog for publishing thoughtful distillations of books and podcasts, featuring a "10 points worth stealing + commentary" format.

## Features

- **Public-Facing Blog**: Clean, minimalist design with chronological post listings
- **Archive with Filters**: Filter posts by author and book/source
- **Series Pages**: Dedicated pages for book series with chapter navigation
- **Writing Interface**: Beautiful, focused writing environment with:
  - Three-pane layout (reference sidebar, main editor, reference pane)
  - Auto-save functionality
  - Preview mode
  - Markdown support for commentary

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a Superuser

```bash
python manage.py createsuperuser
```

This will allow you to:
- Access the Django admin at `/admin/`
- Log in to the writing interface at `/write/login/`

### 4. Collect Static Files

```bash
python manage.py collectstatic
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The site will be available at `http://127.0.0.1:8000/`

## Usage

### Creating Content

1. **Create Authors and Books First**:
   - Go to `/admin/` and create Authors
   - Create Books and link them to Authors
   - Mark books as series if they'll have multiple posts

2. **Write Posts**:
   - Log in at `/write/login/`
   - Click "New Post" to create a post
   - Fill in the form:
     - Title, Date, Author, Book
     - Series order (if part of a series)
     - 10 "Worth Stealing" points
     - Your commentary (markdown supported)
   - Save as draft or publish

3. **View Your Blog**:
   - Homepage: `/`
   - Archive: `/archive/`
   - Series page: `/series/<book-slug>/`
   - Individual post: `/post/<post-slug>/`

## URL Structure

### Public URLs
- `/` - Homepage
- `/archive/` - Archive with filters
- `/series/<book-slug>/` - Series page
- `/post/<post-slug>/` - Individual post
- `/subscribe/` - Newsletter signup (POST)

### Writing Interface (Login Required)
- `/write/` - Dashboard
- `/write/login/` - Login page
- `/write/post/new/` - New post
- `/write/post/<id>/` - Edit post
- `/write/post/<id>/preview/` - Preview post
- `/write/post/<id>/publish/` - Publish post
- `/write/post/<id>/unpublish/` - Unpublish post

## Design

- **Colors**: Warm beige background (#f5f5f0), copper accent (#cc7a52)
- **Typography**: Georgia/Garamond serif for body, system sans-serif for UI
- **Layout**: Minimalist with generous whitespace
- **Special Elements**: 
  - Vertical margin line at 80px
  - Pulsing copper dot
  - Folded corner effects
  - Circular numbered badges

## Models

- **Author**: Blog post authors
- **Book**: Books/podcasts/sources
- **Post**: Blog posts with 10 points and commentary
- **NewsletterSubscriber**: Email subscribers

## Notes

- Posts are stored with JSON fields for the 10 points
- Commentary supports markdown (via markdown2)
- Auto-save runs every 30 seconds and on form changes
- Preview mode shows exactly how the post will look when published

