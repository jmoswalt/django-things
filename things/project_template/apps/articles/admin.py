from django.contrib import admin

from things.admin import ThingAdmin

from articles.models import Article


class ArticleAdmin(ThingAdmin):
    list_display = ['name', 'link', 'content', 'author', 'published_at']


admin.site.register(Article, ArticleAdmin)
