from django.conf.urls import patterns, url

from things.views import ThingDetailView, ThingListView
from .models import Journal

urlpatterns = patterns(
    '',
    url(r'^journals/$',
        ThingListView.as_view(model=Journal),
        name='journal_list'),

    url(r'^journals/(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Journal),
        name='journal_detail'),
)
