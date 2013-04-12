from django.conf.urls import patterns, url

from things.views import ThingDetailView, ThingListView
from .models import Link

urlpatterns = patterns(
    '',
    url(r'^links/$',
        ThingListView.as_view(model=Link),
        name='link_list'),

    url(r'^links/(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Link),
        name='link_detail'),
)
