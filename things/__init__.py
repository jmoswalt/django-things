try:
    from django.conf import settings
    settings.configure()
except RuntimeError:
    pass

from .utils import load_models
load_models()
