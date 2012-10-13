from django.contrib import admin


class ThingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}

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
