from django.conf.urls import patterns, url, include
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from .pages.models import Page
from .views import ThingDetailView, static_build, thing_export
from .feeds import AllThingsFeed, ThingSitemap

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^things/', include(admin.site.urls)),
    url(r'^redactor/', include('redactor.urls')),

    url(r'^deploy/$',
        static_build,
        name='deploy'),
    url(r'^feed/$', AllThingsFeed(), name="feed_all"),
    url(r'^sitemap\.xml$', cache_page(3600)(sitemaps_views.sitemap), {'sitemaps': {'things': ThingSitemap}}),
    url(r'^export/(?P<ct_id>\d+)/$', thing_export, name='things_export'),
    url(r'^(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Page),
        name='page_detail'),
)
