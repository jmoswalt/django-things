from django.conf.urls import patterns, url

from things.views import ThingDetailView, ThingListView
from .models import Post, PostPhoto

urlpatterns = patterns(
    '',
    url(r'^posts/$',
        ThingListView.as_view(model=Post),
        name='post_list'),

    url(r'^posts/(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Post),
        name='post_detail'),

    url(r'^post-photos/(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=PostPhoto),
        name='post_photo_detail'),
)
