import subprocess

from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

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
