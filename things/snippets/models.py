from things.models import Thing, register_thing
from things import attrs, types
from .utils import clear_snippet_cache


class Snippet(Thing):
    cls_attrs = (
        {
            "name": "HTML Allowed",
            "key": "allow_html",
            "description": "If this isn't checked, HTML will be stripped out of the {{ model }}.",
            "datatype": types.TYPE_BOOLEAN,
            "editable": False
        },
        attrs.CONTENT,
    )

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        super(Snippet, self).save(*args, **kwargs)
        clear_snippet_cache(self)


register_thing(Snippet)
