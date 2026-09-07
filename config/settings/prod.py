"""Production settings."""

from decouple import config

from .base import *

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = [
    host.strip()
    for host in config('DJANGO_ALLOWED_HOSTS', default='').split(',')
    if host.strip()
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}