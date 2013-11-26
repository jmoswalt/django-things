from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.forms.models import ModelForm
from django.core.urlresolvers import reverse, NoReverseMatch

from .types import *
from .attrs import *
from .forms import ThingForm, ThingTypeForm
from .models import ThingType


class ThingListFilter(SimpleListFilter):
    title = "Name"
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        result = []
        # TODO
        # qs = model_admin.model.objects.filter(datum__key=self.parameter_name).values('datum__value', 'datum__datatype').order_by('datum__value').distinct()
        # for q in qs:
        #     if not q['datum__value']:
        #         if q['datum__datatype'] == TYPE_BOOLEAN:
        #             result.append((q['datum__value'], "False"))
        #         else:
        #             result.append((q['datum__value'], "(empty)"))
        #     else:
        #         result.append((q['datum__value'], q['datum__value']))
        return tuple(result)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(datum__key=self.parameter_name).filter(datum__value=self.value())
        return queryset


class AuthorListFilter(ThingListFilter):
    title = "Author"
    parameter_name = 'author'


class PrivateListFilter(ThingListFilter):
    title = "Is Private"
    parameter_name = 'private'


class ThingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'list_link', 'add_link', 'import_type', 'export_type')
    prepopulated_fields = {'slug': ['name']}
    form = ThingTypeForm
    fields = [
        'name',
        'slug',
        'json',
        'creator',
        'list_template',
        'detail_template',
    ]

    def count(self, obj):
        return obj.get_class().objects.all().count()

    def list_link(self, obj):
        try:
            link = '<a href="%s" title="View list of items">View List of items</a>' % (
                reverse("admin:things_%s_changelist" % (obj.get_class()._meta.verbose_name.lower())),
            )
        except NoReverseMatch:
            link = ''
        return link
    list_link.allow_tags = True

    def add_link(self, obj):
        try:
            link = '<a href="%s" title="Add list of items">Add List of items</a>' % (
                reverse("admin:things_%s_add" % (obj.get_class()._meta.verbose_name.lower())),
            )
        except NoReverseMatch:
            link = ''
        return link
    add_link.allow_tags = True

    def import_type(self, obj):
        link = '<a href="%s?ct=%s">Import %s</a>' % (
            reverse("things_import"),
            obj.get_class().content_type().pk,
            obj.get_class()._meta.verbose_name_plural.lower(),
        )
        return link
    import_type.allow_tags = True

    def export_type(self, obj):
        if obj.get_class().content_type():
            link = '<a href="%s">Export all %s</a>' % (
                reverse("things_export", kwargs={'ct_id': obj.get_class().content_type().pk}),
                obj.get_class()._meta.verbose_name_plural.lower(),
            )
        else:
            link = ''
        return link
    export_type.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Update the change_view to respect the next querystring
        """
        result = super(ThingTypeAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if not '_addanother' in request.POST and not '_continue' in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result


class ThingAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'slug']
    list_filter = ['published_at', 'updated_at', 'created_at']
    list_per_page = 30

    def __init__(self, *args, **kwargs):
        super(ThingAdmin, self).__init__(*args, **kwargs)

        if self.list_display == ('__str__',):
            thing_fields = ['name', 'link']
            self.list_display = thing_fields + self.model.attrs_list() + ['published_at', 'updated_at']

        if self.form == ModelForm:
            self.form = ThingForm

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
    # for fields in things.attrs
    # --------------------------------- #
    def content(self, obj):
        return truncate_words(strip_tags(obj.get_val(CONTENT)), 15)

    def private(self, obj):
        return bool(obj.get_val(PRIVATE))
    private.boolean = True

    def featured(self, obj):
        return bool(obj.get_val(FEATURED))
    featured.boolean = True

    def image(self, obj):
        if obj.image:
            return '<a href="%s" target="_blank">%s</a>' % (obj.image.url, obj.image.name)
        return ""
    image.allow_tags = True

    # --------------------------------- #
    # DEFAULT METHODS
    # for rendering the form
    # --------------------------------- #
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Update the change_view to respect the next querystring
        """
        result = super(ThingAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
        if not '_addanother' in request.POST and not '_continue' in request.POST and 'next' in request.GET:
            result['Location'] = iri_to_uri("%s") % request.GET.get('next')
        return result

    def get_form(self, request, obj=None, **kwargs):
        form = super(ThingAdmin, self).get_form(request, obj=None, **kwargs)
        form.user = request.user
        return form

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


try:
    admin.site.register(ThingType, ThingTypeAdmin)
except admin.sites.AlreadyRegistered:
    pass
