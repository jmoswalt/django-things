from datetime import datetime

from things import attrs, models, types


ARITCLE_ATTRIBUTES = (
    attrs.CONTENT,
    attrs.AUTHOR,
    attrs.PUBLISHED_AT,
    attrs.FEATURED,
    {
        "name": "Category",
        "key": "category",
        "description": "Add a Category to the {{ model }}.",
        "datatype": types.TYPE_TEXT,
        "required": False
    },
)


class Article(models.Thing):
    public_filter_out = {
        'published_at__gte': 0,
        'published_at__lte': datetime.now().replace(second=0, microsecond=0)
    }
    super_user_order = ['-published_at', '-created_at']
    public_order = "-published_at"

    class Meta:
        proxy = True


models.register_thing(Article, ARITCLE_ATTRIBUTES)
