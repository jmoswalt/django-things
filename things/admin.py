from django.contrib import admin
from django.utils.encoding import iri_to_uri


class ThingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'slug']

    def content(self, obj):
        return obj.content

    def author(self, obj):
        return obj.author

    def link(self, obj):
        link = '<a href="%s" title="View - %s" target="_blank">%s</a>' % (
            obj.get_absolute_url(),
            obj,
            obj.slug,
        )
        return link
    link.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        result = super(ThingAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if not '_addanother' in request.POST and not '_continue' in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result
