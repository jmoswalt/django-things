from things import attrs, models


PAGE_ATTRIBUTES = (
    attrs.CONTENT,
)


class Page(models.Thing):

    class Meta:
        proxy = True


models.register_thing(Page, PAGE_ATTRIBUTES)
