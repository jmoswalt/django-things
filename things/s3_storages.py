import calendar
from datetime import datetime

from boto.utils import parse_ts
from storages.backends.s3boto import S3BotoStorage

from django.conf import settings


class StaticStorage(S3BotoStorage):
    """
    Storage for static files.
    The folder is defined in settings.STATIC_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_S3_PATH
        super(StaticStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        url = super(StaticStorage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url

    def modified_time(self, name):
        name = self._normalize_name(self._clean_name(name))
        entry = self.entries.get(name)
        if entry is None:
            entry = self.bucket.get_key(self._encode_name(name))
        # Parse the last_modified string to a local datetime object.
        return datetime.fromtimestamp(calendar.timegm(parse_ts(entry.last_modified).timetuple()))
