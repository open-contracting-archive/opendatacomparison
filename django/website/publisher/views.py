from django.views.generic import DetailView, ListView

from .models import Publisher


class PublisherListView(ListView):
    model = Publisher


class PublisherDetailView(DetailView):
    model = Publisher
