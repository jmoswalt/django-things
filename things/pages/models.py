from things import attrs, models


PAGE_ATTRIBUTES = (
    attrs.CONTENT,
    attrs.PRIVATE
)


class Page(models.Thing):
    public_filter_out = {'private': ""}

    class Meta:
        proxy = True


models.register_thing(Page, PAGE_ATTRIBUTES)
