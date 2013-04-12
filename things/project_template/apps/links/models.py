from datetime import datetime

from things import attrs, types, models


LINK_ATTRIBUTES = (
    attrs.CONTENT,
    {
        "name": "Link URL",
        "key": "link_url",
        "description": "The URL of the {{ model }}.",
        "required": True,
        "datatype": types.TYPE_TEXT
    },
    {
        "name": "Source Name",
        "key": "source_name",
        "description": "The name of the source for the {{ model }}.",
        "datatype": types.TYPE_TEXT
    },
    {
        "name": "Source URL",
        "key": "source_url",
        "description": "The url of the source for the {{ model }}.",
        "datatype": types.TYPE_TEXT
    },
    attrs.PUBLISHED_AT,
    attrs.PRIVATE,
)


class Link(models.Thing):
    public_filter_out = {
        'private': "",
        'published_at__gte': 0,
        'published_at__lte': datetime.now().replace(second=0, microsecond=0)
    }
    super_user_order = ['-published_at', '-created_at']
    public_order = "-published_at"

    class Meta:
        proxy = True


models.register_thing(Link, LINK_ATTRIBUTES)
