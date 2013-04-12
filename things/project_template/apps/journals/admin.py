from django.contrib import admin

from things.admin import ThingAdmin, AuthorListFilter

from journals.forms import JournalForm
from journals.models import Journal


class JournalAdmin(ThingAdmin):
    form = JournalForm
    list_display = ['name', 'link', 'content', 'author', 'published_at']
    list_filter = [AuthorListFilter]
    ordering = ['-updated_at']


admin.site.register(Journal, JournalAdmin)
