from django.contrib import admin

from things.admin import ThingAdmin

from articles.forms import ArticleForm
from articles.models import Article


class ArticleAdmin(ThingAdmin):
    form = ArticleForm
    list_display = ['name', 'link', 'content', 'author', 'published_at']


admin.site.register(Article, ArticleAdmin)
