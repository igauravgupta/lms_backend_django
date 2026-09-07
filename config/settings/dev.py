"""Development settings."""

from decouple import config

from .base import *

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = [
	host.strip()
	for host in config('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')
	if host.strip()
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}