from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
)

from braces.views import LoginRequiredMixin

from .models import Datamap, Field


class DatamapListView(ListView):
    model = Datamap


class DatamapAddView(LoginRequiredMixin, CreateView):
    model = Datamap


class DatamapEditView(LoginRequiredMixin, UpdateView):
    model = Datamap
