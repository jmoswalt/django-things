from math import ceil

from django_medusa.renderers import StaticSiteRenderer
from .models import Thing


class ThingRenderer(StaticSiteRenderer):
    def get_paths(self):
        # A "set" so we can throw items in blindly and be guaranteed that
        # we don't end up with dupes.
        paths = set(['/'])

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
                if subclass._meta.app_label != "pages":
                    list_view = "/%s/" % subclass._meta.app_label
                    paths.add(list_view)
                    # Add in paginated pages
                    for p in xrange(int(ceil(subclass.objects.count()/float(20)))):
                        paths.add("%s%s/" % (list_view, (p + 1)))
                for item in subclass.objects.filter(**subclass.public_filter_out):
                    # Thing detail view
                    paths.add(item.get_absolute_url())

        # Cast back to a list since that's what we're expecting.
        return list(paths)

renderers = [ThingRenderer, ]
