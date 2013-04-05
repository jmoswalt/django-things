from django.conf import settings

from .utils import load_theme_snippets

load_theme_snippets(settings.THEME_PATH)
