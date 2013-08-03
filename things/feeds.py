from django.contrib.syndication.views import Feed
from django.contrib.sitemaps import Sitemap
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone

from .models import Thing
from .utils import get_thing_objects_qs


class ThingFeed(Feed):
    model = Thing

    def items(self):
        return get_thing_objects_qs(self.model)

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.name

    def item_pubdate(self, item):
        return item.created_at

    def item_link(self, item):
        return item.get_absolute_url()


class AllThingsFeed(Feed):
    title = "%s" % Site.objects.get_current().name
    link = "/feed/"
    description = "Latest Content from http://%s/" % Site.objects.get_current().domain

    def __init__(self):
        Feed.__init__(self)
        self.feed_for_item = {}

    def load_feeds_items(self):
        """
        Combine subclasses to get combined feed
        """
        self.all_items = []
        feeds = get_thing_subfeeds()
        for feed in feeds:
            feed()
            feed_instance = feed()
            item_per_feed_cnt = 0
            for item in feed_instance.items():
                self.feed_for_item[item] = feed_instance
                self.all_items.append((item, timezone.make_aware(self.item_pubdate(item), timezone.utc)))
                item_per_feed_cnt += 1
                if item_per_feed_cnt >= 20:
                    break

    def items(self):
        self.load_feeds_items()
        sorted_items = sorted(self.all_items, key=lambda thing: thing[1], reverse=True)
        items = [i[0] for i in sorted_items]
        return items[:20]

    def item_title(self, item):
        return self.get_attr_item('title', item)

    def item_description(self, item):
        return self.get_attr_item('description', item)

    def item_pubdate(self, item):
        return self.get_attr_item('pubdate', item)

    def item_link(self, item):
        return self.get_attr_item('link', item)

    def get_attr_item(self, attr, item):
        """
        Gets the value for the item_attribute for the item
        """
        if item in self.feed_for_item:
            feed = self.feed_for_item[item]
            method_name = 'item_' + attr
            if hasattr(feed, method_name):
                method = getattr(feed, method_name)
                return method.__func__(feed, item)
        return None


def get_thing_subfeeds():
    for app in settings.THINGS_APPS:
        try:
            __import__(".".join([app, "feeds"]))
        except ImportError:
            pass
    ThingFeed.__subclasses__()
    return ThingFeed.__subclasses__()


class ThingSitemap(Sitemap):
    changefreq = "never"
    priority = 0.4

    def items(self):
        items = []
        apps = Thing.content_apps()
        for app in apps:
            query = get_thing_objects_qs(app)
            for item in query:
                items.append(item)

        return items

    def lastmod(self, obj):
        return obj.updated_at
