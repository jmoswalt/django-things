from django.contrib import admin

from things.admin import ThingAdmin, PrivateListFilter

from .models import Page


class PageAdmin(ThingAdmin):
    list_filter = [PrivateListFilter]


admin.site.register(Page, PageAdmin)
