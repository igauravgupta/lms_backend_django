"""
config/settings/__init__.py
 
Normally this stays empty — it just makes `config.settings` a package so
Python can import `config.settings.dev`, `config.settings.staging`, and
`config.settings.prod` directly.
 
The recommended way to select an environment is to point
DJANGO_SETTINGS_MODULE straight at the file you want:
 
    export DJANGO_SETTINGS_MODULE=config.settings.dev
    export DJANGO_SETTINGS_MODULE=config.settings.prod
 
That's explicit, greppable, and hard to get wrong."""

from decouple import config

settings_module = config('DJANGO_SETTINGS_MODULE', default='')

if settings_module.endswith('.prod'):
    from .prod import *
else:
    from .dev import *
