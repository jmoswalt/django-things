from django.contrib import admin


class ThingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}

    def content(self, obj):
        return obj.content

    def author(self, obj):
        return obj.author

    def view_on_site(self, obj):
        link = '<a href="%s" title="View - %s" target="_blank">View</a>' % (
            obj.get_absolute_url(),
            obj,
        )
        return link
    view_on_site.allow_tags = True
    view_on_site.short_description = 'view'
