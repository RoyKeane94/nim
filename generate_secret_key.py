#!/usr/bin/env python
"""
Helper script to generate a secure Django SECRET_KEY.
Run this script and copy the output to your .env file.
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("Generated SECRET_KEY:")
    print("="*70)
    print(secret_key)
    print("="*70)
    print("\nCopy this value to your .env file as:")
    print(f"SECRET_KEY={secret_key}\n")
