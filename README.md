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

### Development Setup

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up Environment Variables**

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and set your `SECRET_KEY`. Generate a secure key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

5. **Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a Superuser**

```bash
python manage.py createsuperuser
```

This will allow you to:
- Access the Django admin at `/admin/`
- Log in to the writing interface at `/write/login/`

7. **Collect Static Files**

```bash
python manage.py collectstatic
```

8. **Run the Development Server**

```bash
python manage.py runserver
```

The site will be available at `http://127.0.0.1:8000/`

### Production Deployment

#### Prerequisites

- Python 3.8+
- A production-ready database (PostgreSQL recommended)
- A web server (Nginx, Apache, or similar)
- A WSGI server (Gunicorn, uWSGI, or similar)

#### Steps

1. **Set up PostgreSQL Database**

Install PostgreSQL and create a database:

```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE nim_db;
CREATE USER nim_user WITH PASSWORD 'your-secure-password';
ALTER ROLE nim_user SET client_encoding TO 'utf8';
ALTER ROLE nim_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nim_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nim_db TO nim_user;
\q
```

2. **Set Environment Variables**

Create a `.env` file with production settings:

```bash
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration (required for production)
DB_NAME=nim_db
DB_USER=nim_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
X_FRAME_OPTIONS=DENY

# Email Settings (optional)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Run Migrations**

```bash
python manage.py migrate
```

4. **Collect Static Files**

WhiteNoise will serve static files, but you need to collect them first:

```bash
python manage.py collectstatic --noinput
```

5. **Run with Gunicorn**

```bash
pip install gunicorn
gunicorn nim.wsgi:application --bind 0.0.0.0:8000
```

#### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `SECRET_KEY` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up SSL/HTTPS (required for security settings)
- [ ] Install and configure PostgreSQL database
- [ ] Set `DATABASE_URL` or individual database settings in `.env`
- [ ] Run migrations on production database
- [ ] Set up proper logging
- [ ] Configure email backend if using newsletter features
- [ ] Set up a reverse proxy (Nginx/Apache) in front of Gunicorn
- [ ] Set up process management (systemd, supervisor, etc.)
- [ ] Configure backup strategy for database
- [ ] Set up monitoring and error tracking

#### Database Notes

- **Development**: Automatically uses SQLite (`db.sqlite3`) when `DEBUG=True`
- **Production**: Automatically uses PostgreSQL when `DEBUG=False`
- You can override this behavior by explicitly setting `DATABASE_URL` in development if needed
- Make sure `psycopg2-binary` is installed (included in requirements.txt)

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

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

