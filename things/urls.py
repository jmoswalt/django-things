from django.conf.urls import patterns, url

from .pages.models import Page
from .views import ThingDetailView, static_build
from .feeds import AllThingsFeed


urlpatterns = patterns(
    '',
    url(r'^deploy/$',
        static_build,
        name='deploy'),
    url(r'^feed/$', AllThingsFeed()),
    url(r'^(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Page),
        name='page_detail'),
)
