import subprocess
import json
from dateutil.parser import parse
from datetime import datetime

from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import timezone

from braces.views import StaffuserRequiredMixin

from .utils import get_thing_object, get_thing_objects_qs
from .forms import ThingImportForm
from .models import ThingType, Thing
from .types import TYPE_TEXT, TYPE_LONGTEXT, TYPE_DATE, TYPE_BOOLEAN


class ThingDetailView(DetailView):
    default_template_name = "things/thing_detail.html"

    def get_object(self, **kwargs):
        return get_thing_object(self.model, self.kwargs['slug'], self.request.user)

    def get_template_names(self):
        names = []

        names.append("%s/%s%s.html" % (
            self.model._meta.app_label,
            self.model._meta.object_name.lower(),
            self.template_name_suffix)
        )

        names.append(self.default_template_name)
        return names

    def get_context_data(self, **kwargs):
        context = super(ThingDetailView, self).get_context_data(**kwargs)
        context['object_type'] = self.model._meta.verbose_name
        context['object_type_plural'] = self.model._meta.verbose_name_plural
        context['extend_things'] = self.default_template_name

        return context


class ThingListView(ListView):
    default_template_name = "things/thing_list.html"

    def get_queryset(self, *args, **kwargs):
        super(ThingListView, self).get_queryset(*args, **kwargs)
        return get_thing_objects_qs(self.model, self.request.user)

    def get_template_names(self):
        names = []

        names.append("%s/%s%s.html" % (
            self.model._meta.app_label,
            self.model._meta.object_name.lower(),
            self.template_name_suffix)
        )

        names.append(self.default_template_name)
        return names

    def get_context_data(self, **kwargs):
        context = super(ThingListView, self).get_context_data(**kwargs)
        context['object_type'] = self.model._meta.verbose_name
        context['object_type_plural'] = self.model._meta.verbose_name_plural
        context['extend_things'] = self.default_template_name

        return context


@staff_member_required
def static_build(request):
    subprocess.Popen(["python", "manage.py", "rebuild_static_site"])
    messages.success(request, 'Static Build triggered')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@staff_member_required
def thing_export(request, ct_id):
    """
    Create a JSON export of all of the selected kind of Thing.
    """
    content_type = get_object_or_404(ContentType, id=ct_id)
    filename = "%ss_%s.json" % (content_type.model, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    items = []
    all_things = content_type.model_class().objects.all().order_by('created_at')

    if all_things:
        fields = all_things[0].attrs_list()
        # for field in fields:
        #     columns.append(field)
        # csv_file.writerow(columns)

        for t in all_things:
            row = {}
            row['name'] = t.name
            row['slug'] = t.slug
            row['created_at'] = t.created_at.strftime("%Y-%m-%d %H:%M:%S")
            row['updated_at'] = t.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if t.published_at:
                row['published_at'] = t.published_at.strftime("%Y-%m-%d %H:%M:%S")
            row['username'] = getattr(t.creator, 'username', '')

            for field in fields:
                val = getattr(t, field, '')
                if type(val) == datetime:
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                row[field] = val
            items.append(row)

    response = HttpResponse(json.dumps(items), mimetype='application/json')
    response["Content-Disposition"] = "attachment; filename=%s" % filename

    return response


class ThingImportView(StaffuserRequiredMixin, FormView):
    template_name = 'admin/import.html'
    form_class = ThingImportForm

    def form_valid(self, form):
        hard_keys = ['name', 'slug', 'created_at', 'updated_at', 'published_at', 'username']
        add_count = 0
        found_count = 0

        upload_file = form.cleaned_data['upload_file']
        data = json.load(upload_file)

        if form.cleaned_data['thing_type']:
            type_msg = "type"
            model = ContentType.objects.get(pk=form.cleaned_data['thing_type']).model_class()
        elif form.cleaned_data['thing_type_name']:
            type_msg = "new type"
            new_type = ThingType()
            new_type.name = form.cleaned_data['thing_type_name']
            new_type.slug = slugify(form.cleaned_data['thing_type_name'])
            new_type.creator = self.request.user
            new_type_fields = []
            for k in data[0].keys():
                if k not in hard_keys:
                    # Try to detect datatype
                    if type(data[0][k]) == bool:
                        datatype = TYPE_BOOLEAN
                    elif len(data[0][k]) > 50:
                        datatype = TYPE_LONGTEXT
                    else:
                        try:
                            parse(data[0][k])
                            datatype = TYPE_DATE
                        except ValueError:
                            datatype = TYPE_TEXT

                    new_type_fields.append({
                        'name': k.title(),
                        'key': slugify(k),
                        'datatype': datatype
                    })

            new_type.json = {
                'fields': new_type_fields,
                }
            new_type.save()
            model = new_type.get_class()

        for d in data:
            new_item = {}
            new_item['name'] = d['name']
            new_item['content_type_id'] = model.content_type().pk
            new_item['slug'] = d.get('slug', slugify(new_item['name']))

            # Check if slug exists for this model, so a match is found
            # instead of adding it again
            try:
                slug_exists = model.objects.get(slug=new_item['slug'])
                if slug_exists:
                    exists = True
            except:
                # Slug does not exist for this model. Check all models
                # to see if this slug exists
                try:
                    i = 0
                    exists = True
                    original_slug = new_item['slug']
                    while exists:
                        if i == 0:
                            slug = original_slug
                        else:
                            slug = original_slug + str(i)
                        new_item['slug'] = slug
                        exists = Thing.all_things.get(slug=slug)
                        if exists:
                            i = i + 1
                except Thing.DoesNotExist:
                    pass

            item, created = model.objects.get_or_create(**new_item)
            if created:
                add_count = add_count + 1
                item.creator = self.request.user

                for field in model._meta.fields:
                    if field.name == "updated_at":
                        field.auto_now = False

                if 'created_at' in d:
                    item.created_at = timezone.make_aware(parse(d['created_at']), timezone.utc)

                if 'updated_at' in d:
                    item.updated_at = timezone.make_aware(parse(d['updated_at']), timezone.utc)
                else:
                    item.updated_at = timezone.now()

                if 'published_at' in d:
                    item.published_at = timezone.make_aware(parse(d['published_at']), timezone.utc)

                item_json = {}
                for k in d.keys():
                    if k not in hard_keys:
                        item_json[k] = d[k]
                item.json = item_json
                item.save(rebuild=False)

                for field in model._meta.fields:
                    if field.name == "updated_at":
                        field.auto_now = True

            else:
                found_count = found_count + 1

        messages.success(self.request, 'Successfully imported to %s "%s". %s added, %s already found (not updated).' % (type_msg, model._meta.verbose_name_plural.lower(), add_count, found_count))

        if settings.USE_STATIC_SITE:
            subprocess.Popen(["python", "manage.py", "rebuild_static_site"])

        try:
            self.success_url = reverse("admin:%s_%s_changelist" % (model._meta.app_label, model._meta.verbose_name.lower()))
        except NoReverseMatch:
            pass

        return super(ThingImportView, self).form_valid(form)

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']
        if self.success_url:
            return self.success_url
        return reverse('admin:index')
