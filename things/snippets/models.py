from things.models import Thing, register_thing
from things import attrs, types


TEMPLATE_TEXT_ATTRIBUTES = (
    {
        "name": "HTML Allowed",
        "key": "allow_html",
        "description": "If this isn't checked, HTML will be stripped out of the {{ model }}.",
        "datatype": types.TYPE_BOOLEAN,
        "editable": False
    },
    attrs.CONTENT,
)


class Snippet(Thing):

    class Meta:
        proxy = True


register_thing(Snippet, TEMPLATE_TEXT_ATTRIBUTES)
