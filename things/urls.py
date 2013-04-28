from django.conf.urls import patterns, url
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page

from .pages.models import Page
from .views import ThingDetailView, static_build
from .feeds import AllThingsFeed, ThingSitemap


urlpatterns = patterns(
    '',
    url(r'^deploy/$',
        static_build,
        name='deploy'),
    url(r'^feed/$', AllThingsFeed(), name="feed_all"),
    url(r'^sitemap\.xml$', cache_page(3600)(sitemaps_views.sitemap), {'sitemaps': {'things': ThingSitemap}}),
    url(r'^(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Page),
        name='page_detail'),
)
