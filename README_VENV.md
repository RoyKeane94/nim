# Virtual Environment Setup

## Current Location
The virtual environment (`venv/`) is located in the same directory as `manage.py`, which is the correct location.

## Activating the Virtual Environment

From the project root (`/Users/tombarratt/Desktop/Coding_Projects/nim/nim/`):

```bash
# Navigate to the Django project directory
cd /Users/tombarratt/Desktop/Coding_Projects/nim/nim

# Activate the virtual environment
source venv/bin/activate
```

Or if you're already in the `nim` directory:

```bash
source venv/bin/activate
```

## Verifying Activation

After activation, you should see `(venv)` in your terminal prompt:

```bash
(venv) tombarratt@Toms-Laptop nim %
```

## Why This Location?

The virtual environment is in the same directory as `manage.py` because:
1. It's the Django project root
2. All project files (settings, apps, requirements.txt) are here
3. It's already in `.gitignore`, so it won't be committed
4. It's the standard Django project structure

## Alternative: Moving venv to Parent Directory

If you prefer to have the venv at `/Users/tombarratt/Desktop/Coding_Projects/nim/venv`, you can:

1. Move it: `mv nim/venv ../venv`
2. Update your activation: `source ../venv/bin/activate`

However, keeping it with `manage.py` is the recommended approach.
