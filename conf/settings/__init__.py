"""
Settings initialization for railway_project.

Automatically loads the appropriate settings module based on DJANGO_SETTINGS_MODULE
or defaults to development settings.
"""

import os

# Determine which settings module to use
# By default, use development settings
# In production, set DJANGO_SETTINGS_MODULE=railway_project.settings.production
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'railway_project.settings.development')

if 'development' in settings_module:
    from .development import *
elif 'production' in settings_module:
    from .production import *
else:
    # Default to development if not specified
    from .development import *
