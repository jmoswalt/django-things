from django.contrib import admin

from things.models import Page
from things.forms import PageForm


class ThingAdmin(admin.ModelAdmin):

    def content(self, obj):
        return obj.content

    def author(self, obj):
        return obj.author


class PageAdmin(ThingAdmin):
    form = PageForm
    list_display = ['name', 'content', 'create_dt']
    fields = ['name', 'content']


admin.site.register(Page, PageAdmin)
