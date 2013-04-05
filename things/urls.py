from django.conf.urls import patterns, url

from things.pages.models import Page
from things.views import ThingDetailView

urlpatterns = patterns(
    '',
    url(r'^(?P<slug>[\w\-\/]+)/$',
        ThingDetailView.as_view(model=Page),
        name='page_detail'),
)
