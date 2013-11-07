from math import ceil
from datetime import datetime

from django_medusa.renderers import StaticSiteRenderer
from django.utils import timezone
from django.conf import settings
from .models import Thing, StaticBuild
from snippets.models import Snippet


class ThingRenderer(StaticSiteRenderer):
    def get_paths(self):
        # A "set" so we can throw items in blindly and be guaranteed that
        # we don't end up with dupes.
        paths = set(['/', '/feed/', '/sitemap.xml'])

        for subclass in Thing.__subclasses__():
            # Special case for built-in pages module
            if subclass._meta.app_label == "pages":
                has_urls = True
            else:
                try:
                    __import__('.'.join([subclass._meta.app_label, 'urls']))
                    has_urls = True
                except ImportError:
                    print "No urls for %s found" % subclass._meta.app_label
                    has_urls = False

            if has_urls:
                # Get the latest StaticBuild time to see what we need to rebuild
                rebuild_list = False
                latest_static_build = StaticBuild.objects.order_by('-created_at')
                if latest_static_build:
                    dt = latest_static_build[0].created_at
                else:
                    dt = timezone.make_aware(datetime(1, 1, 1), timezone.get_current_timezone())

                # if a snippet changes, rebuild everything
                snips = Snippet.objects.filter(updated_at__gte=dt)

                for item in subclass.objects.filter(**subclass.public_filter_out):
                    # Thing detail view
                    # Only add the path if a snippet has been changed or if
                    # the item had been updated since the last build.
                    if item.updated_at > dt or snips:
                        paths.add(item.get_absolute_url())
                        if settings.FULL_STATIC_SITE:
                            rebuild_list = True

                if subclass._meta.app_label != "pages":
                    if rebuild_list:
                        list_view = "/%s/" % subclass._meta.app_label
                        paths.add(list_view)
                        # Add in paginated pages
                        for p in xrange(int(ceil(subclass.objects.count()/float(20)))):
                            paths.add("%s%s/" % (list_view, (p + 1)))

        # Cast back to a list since that's what we're expecting.
        return list(paths)

renderers = [ThingRenderer, ]
