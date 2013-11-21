import subprocess
from csv import writer
from datetime import datetime

from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .utils import get_thing_object, get_thing_objects_qs


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
    Create a CSV export of all of the selected kind of Thing.
    """
    content_type = get_object_or_404(ContentType, id=ct_id)
    response = HttpResponse(mimetype="text/csv")
    csvname = "%ss_%s.csv" % (content_type.model, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    response["Content-Disposition"] = "attachment; filename=%s" % csvname
    csv = writer(response)

    default_columns = ['name', 'slug', 'created_at', 'updated_at', 'username']
    columns = default_columns
    all_things = content_type.model_class().objects.all().order_by('created_at')

    if all_things:
        fields = all_things[0].attrs_list()
        for field in fields:
            columns.append(field)
        csv.writerow(columns)

        for t in all_things:
            row = []
            row.append(t.name)
            row.append(t.slug)
            row.append(t.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            row.append(t.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            row.append(getattr(t.creator, 'username', ''))

            for field in fields:
                row.append(getattr(t, field, ''))

            for x in range(len(columns) - len(row)):
                row.append('')

            # Write out the row.
            csv.writerow(row)
    return response
