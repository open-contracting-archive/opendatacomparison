from django.views.generic import (
    CreateView,
    UpdateView,
)

from braces.views import LoginRequiredMixin

from .models import Datamap, Field


class DatamapAddView(LoginRequiredMixin, CreateView):
    model = Datamap


class DatamapEditView(LoginRequiredMixin, UpdateView):
    model = Datamap
