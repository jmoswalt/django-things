from django.conf.urls import patterns, url

from things.pages import views

urlpatterns = patterns(
    '',
    url(r'^(?P<slug>[\w\-\/]+)/$', views.PageDetailView.as_view(), name='page_detail'),
)
