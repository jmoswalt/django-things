from django.conf.urls import patterns, url, include
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, base

from .pages.models import Page
from .views import ThingListView, ThingDetailView, ThingImportView, static_build, thing_export
from .feeds import AllThingsFeed, ThingSitemap

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^things/import/$', ThingImportView.as_view(), name='things_import'),
    url(r'^things/', include(admin.site.urls)),
    url(r'^accounts/login/$', base.RedirectView.as_view(), {'url': '/'}),
    url(r'^redactor/', include('redactor.urls')),
    url(r'^deploy/$',
        static_build,
        name='deploy'),
    url(r'^feed/$', AllThingsFeed(), name="feed_all"),
    url(r'^sitemap\.xml$', cache_page(3600)(sitemaps_views.sitemap), {'sitemaps': {'things': ThingSitemap}}),
    url(r'^export/(?P<ct_id>\d+)/$', thing_export, name='things_export'),
)

def auto_app_url_patterns():
    from .models import ThingType
    items = []
    things = ThingType.objects.all()
    for t in things:
        thing = t.get_class()
        label = thing._meta.verbose_name.lower()
        label_p = thing._meta.verbose_name_plural.lower()
        listname = '%s_list' % label
        detailname = '%s_detail' % label
        items.append(url(r'^%s/([\d]+)?/?$' % label_p, ThingListView.as_view(model=thing), name=listname))
        items.append(url(r'^%s/(?P<slug>[\w\-]+)/$' % label_p, ThingDetailView.as_view(model=thing), name=detailname))

    return items

urlpatterns += auto_app_url_patterns()

urlpatterns += patterns('',
    url(r'^(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Page),
        name='page_detail'),
    )
