from django.conf.urls import patterns, url

from things.views import ThingDetailView, ThingListView
from .models import Article


urlpatterns = patterns(
    '',
    url(r'^articles/([\d]+)?/?$',
        ThingListView.as_view(model=Article),
        name='article_list'),

    url(r'^articles/(?P<slug>[\w\-]+)/$',
        ThingDetailView.as_view(model=Article),
        name='article_detail'),
)
