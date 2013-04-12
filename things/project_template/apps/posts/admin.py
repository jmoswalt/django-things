from django.contrib import admin

from things.admin import ThingAdmin

from .models import Post, PostPhoto


class PostPhotoAdmin(ThingAdmin):
    list_display = ['name', 'link', 'image', 'post_link']

    def post_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.post.get_absolute_url(), obj.post)
    post_link.allow_tags = True

admin.site.register(Post, ThingAdmin)
admin.site.register(PostPhoto, PostPhotoAdmin)
