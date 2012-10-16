from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words


class ThingListFilter(SimpleListFilter):
    title = "Name"
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        result = []
        qs = model_admin.model.objects.filter(datum__key=self.parameter_name).values('datum__value').order_by('datum__value').distinct()
        for q in qs:
            if not q['datum__value']:
                result.append((q['datum__value'], "(empty)"))
            else:
                result.append((q['datum__value'], q['datum__value']))
        return tuple(result)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(datum__key=self.parameter_name).filter(datum__value=self.value())
        return queryset


class ThingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'slug']
    list_display = ['name', 'link', 'updated_at']

    def link(self, obj):
        """
        Field display method to output of the slug field
        to link to get_absolute_url.
        """
        link = '<a href="%s" title="View - %s" target="_blank">%s</a>' % (
            obj.get_absolute_url(),
            obj,
            obj.slug,
        )
        return link
    link.allow_tags = True

    # --------------------------------- #
    # HELPER METHODS
    # for common field names
    # --------------------------------- #
    def content(self, obj):
        return truncate_words(obj.content, 15)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Update the change_view to respect the next querystring
        """
        result = super(ThingAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if not '_addanother' in request.POST and not '_continue' in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        This is awesome and comes from django-eav
        https://github.com/mvpdev/django-eav/blob/master/eav/admin.py#L32

        Wrapper for ModelAdmin.render_change_form. Replaces standard static
        AdminForm with an EAV-friendly one. The point is that our form generates
        fields dynamically and fieldsets must be inferred from a prepared and
        validated form instance, not just the form class. Django does not seem
        to provide hooks for this purpose, so we simply wrap the view and
        substitute some data.
        """
        form = context['adminform'].form

        # infer correct data from the form
        fieldsets = self.fieldsets or [(None, {'fields': form.fields.keys()})]
        adminform = admin.helpers.AdminForm(form, fieldsets,
                                      self.prepopulated_fields)
        media = mark_safe(self.media + adminform.media)

        context.update(adminform=adminform, media=media)

        super_meth = super(ThingAdmin, self).render_change_form
        return super_meth(request, context, add, change, form_url, obj)
