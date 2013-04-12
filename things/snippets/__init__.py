from django.conf import settings
from things.settings import THINGS_ROOT

from .utils import load_theme_snippets

load_theme_snippets(settings.THEME_PATH)
load_theme_snippets(THINGS_ROOT)
