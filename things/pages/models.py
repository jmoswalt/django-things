from things.models import Thing, register_thing
from things import attrs


PAGE_ATTRIBUTES = (
    attrs.CONTENT,
    attrs.PRIVATE
)


class Page(Thing):

    class Meta:
        proxy = True


register_thing(Page, PAGE_ATTRIBUTES)
