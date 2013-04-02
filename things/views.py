from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from .utils import get_thing_object_or_404


class ThingDetailView(DetailView):
    public_filter_out = {}

    def get_object(self, **kwargs):
        super(ThingDetailView, self).get_object(**kwargs)
        if self.request.user.is_superuser:
            obj = get_object_or_404(self.model, slug=self.kwargs['slug'])

        else:
            filters = self.public_filters
            obj = get_thing_object_or_404(
                cls=self.model,
                slug=self.kwargs['slug'],
                **filters)

        return obj

    def get_template_names(self):
        names = []

        names.append("%s/%s%s.html" % (
            self.model._meta.app_label,
            self.model._meta.object_name.lower(),
            self.template_name_suffix)
        )

        names.append("things/thing_detail.html")
        return names


class ThingListView(ListView):
    public_filter_out = {}
    super_user_order = ['-created_at']
    public_order = ""

    def get_queryset(self, *args, **kwargs):
        super(ThingListView, self).get_queryset(*args, **kwargs)
        if self.request.user.is_superuser:
            queryset = self.model.objects.order_by(*self.super_user_order)
        else:
            queryset = self.model.objects.filter(**self.public_filter_out)

            if self.public_order:
                if self.public_order.replace('-', '') in self.model.attrs_list():
                    if self.public_order[0] == "-":
                        key = self.public_order[1:]
                        value = '-datum__value'
                    else:
                        key = self.public_order
                        value = 'datum_value'

                    queryset = queryset.filter(datum__key=key).order_by(value)
                else:
                    queryset = queryset.order_by(self.public_order)

        return queryset

    def get_template_names(self):
        names = []

        names.append("%s/%s%s.html" % (
            self.model._meta.app_label,
            self.model._meta.object_name.lower(),
            self.template_name_suffix)
        )

        names.append("things/thing_list.html")
        return names
