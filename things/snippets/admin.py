from django.contrib import admin

from things.admin import ThingAdmin

from .models import Snippet
from .forms import SnippetForm


class SnippetAdmin(ThingAdmin):
    form = SnippetForm
    list_display = ['name', 'slug', 'content', 'allow_html', 'updated_at']

admin.site.register(Snippet, SnippetAdmin)
