from os.path import join

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^redactor/', include('redactor.urls')),
)


# Include urls to catch media requests in case
# the web server (nginx/apache/etc.) isn't setup
urlpatterns += patterns(
    '',
    (r'^static/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': join(settings.PROJECT_ROOT, 'static')}
     ),
    (r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': join(settings.PROJECT_ROOT, 'media')}
     ),
)


# Automatically try to load url patterns from the
# THINGS_APPS and append them to the list.
def get_app_url_patterns():
    items = []
    apps = settings.THINGS_APPS
    for app in apps:
        try:
            __import__('.'.join([app, 'urls']))
            items.append((r'', include('%s.urls' % app,)))
        except ImportError:
            pass

    return patterns('', *items)

urlpatterns += get_app_url_patterns()

# Things urls come last because they include the
# pages urls which are pretty wide open
urlpatterns += url(r'^', include('things.urls')),
