from things.views import ThingDetailView
from .models import Page


PUBLIC_FILTER_OUT = {'private': ""}


class PageDetailView(ThingDetailView):
    model = Page
    public_filter_out = PUBLIC_FILTER_OUT
